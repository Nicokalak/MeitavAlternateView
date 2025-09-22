import http
import io
import json
import logging
import os
import sys
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

import pandas as pd
import requests
from flask import Flask, Response, abort, jsonify, request, send_from_directory
from waitress import serve

from meitav_view.model.config import Config
from meitav_view.model.stock import Stock
from meitav_view.utils import auth_utils
from meitav_view.utils.auth_utils import require_authentication
from meitav_view.utils.trends_persist import TrendPersist
from meitav_view.utils.yahoo_requestor import YahooRequestor


class AppGlobs:
    stocks_cache: List[Stock] = list()
    trends: Dict[str, Any] = {"PRE_histo": {}, "REGULAR_histo": {}, "POST_histo": {}}
    lock = threading.Lock()
    config_lock = threading.Lock()
    time_format: str
    config: Config
    logger: logging.Logger
    persist: TrendPersist


app = Flask(__name__, static_url_path="/static/")
g = AppGlobs()


@app.route("/trends")
@require_authentication
def get_trends() -> Dict[str, Any]:
    return g.trends


def get_portfolio_table() -> Optional[str]:
    try:
        attempts = 0
        r = requests.get(
            os.getenv("portfolio_link", ""),
            headers={"User-Agent": "Meitav-Viewer/{}".format(os.getenv("HOSTNAME"))},
        )
        while (
            attempts < g.config.get("retry_attempts", 3)
            and r.status_code != http.HTTPStatus.OK.value
        ):
            attempts += 1
            g.logger.error(
                "failed to get portfolio from Meitav attempt {} stats {} {}".format(
                    attempts, r.status_code, r.text
                )
            )
            r = requests.get(
                os.getenv("portfolio_link", ""),
                headers={
                    "User-Agent": "Meitav-Viewer/{}".format(os.getenv("HOSTNAME"))
                },
            )
        return r.text
    except ConnectionError as e:
        g.logger.error("failed to connect to meitav", e)
        return None


def add_trend(trends_obj: Dict[str, Any], change_key: str) -> None:
    trends_obj["trend"] = 0
    trends_obj["watchlist_trend"] = 0
    m_state = trends_obj["marketState"]
    state_histo = m_state + "_histo"
    watchlist_sum = 0.0
    watchlist_count = 0.0
    if m_state in ("CLOSED", "PREPRE", "POSTPOST"):
        return
    for s in g.stocks_cache:
        yahoo_symbol_data = s.api_data
        trends_obj["trend"] += s.day_val if s.type != "W" else 0
        if s.type == "W":
            watchlist_sum += s.percent_change
            watchlist_count += 1
            trends_obj["watchlist_trend"] = watchlist_sum / watchlist_count
        if change_key in yahoo_symbol_data:
            if s.type == "W":
                continue
            if s.type == "E":
                trends_obj["yahoo_trend"] += yahoo_symbol_data[change_key] * s.quantity
            elif m_state == "REGULAR":
                trends_obj["yahoo_trend"] += s.day_val
    trends_for_chart(state_histo, trends_obj["yahoo_trend"])
    g.persist.save()


def trends_for_chart(state_histo_key: str, histo_val: float) -> None:
    curr_histo = g.trends[state_histo_key]

    to_delete = []
    for key, state_histo in g.trends.items():
        for date in state_histo.keys():
            if (datetime.now() - datetime.strptime(date, g.time_format)) > timedelta(
                days=1, seconds=43200
            ):
                to_delete.append((key, date))
    for tup in to_delete:
        del g.trends[tup[0]][tup[1]]

    curr_histo[datetime.now().strftime(g.time_format)] = histo_val


def get_market_state_key(market_state: str = "post") -> str:
    return (
        market_state.lower()
        if market_state.lower() in ("pre", "post", "regular")
        else "post"
    )


@app.route("/marketState")
@require_authentication
def get_market_state() -> Dict[str, Any]:
    if len(g.stocks_cache) == 0:
        abort(http.HTTPStatus.INTERNAL_SERVER_ERROR.value)

    result = {
        "marketState": g.stocks_cache[0].api_data.get("marketState"),
        "trend": 0,
        "yahoo_trend": 0,
    }
    change = (
        get_market_state_key(g.stocks_cache[0].api_data.get("marketState", ""))
        + "MarketChange"
    )
    change_per = (
        get_market_state_key(g.stocks_cache[0].api_data.get("marketState", ""))
        + "MarketChangePercent"
    )
    add_trend(result, change)
    result["top-gainer"] = max(
        g.stocks_cache, key=lambda s: s.api_data.get(change, 0) * s.quantity
    )
    result["top-gainer%"] = max(
        g.stocks_cache, key=lambda s: s.api_data.get(change_per, 0)
    )
    result["top-loser"] = min(
        g.stocks_cache, key=lambda s: s.api_data.get(change, 0) * s.quantity
    )
    result["top-loser%"] = min(
        g.stocks_cache, key=lambda s: s.api_data.get(change_per, 0)
    )
    result["top-mover"] = max(
        g.stocks_cache, key=lambda s: s.api_data.get("regularMarketVolume", 0)
    )
    result["up-down"] = {
        "up": len(
            list(filter(lambda sd: sd.gain is not None and sd.gain > 0, g.stocks_cache))
        ),
        "down": len(
            list(filter(lambda sd: sd.gain is not None and sd.gain < 0, g.stocks_cache))
        ),
    }
    result["trending"] = max(
        g.stocks_cache,
        key=lambda s: s.api_data.get("regularMarketVolume", 0)
        / s.api_data.get("averageDailyVolume10Day", sys.maxsize),
    )
    return result


@app.route("/portfolio")
@require_authentication
def get_enriched_portfolio() -> List[Stock]:
    with g.lock:
        g.logger.info(
            "request for portfolio from: {} {}".format(
                request.headers.get("X-Real-Ip"), request.headers.get("User-Agent")
            )
        )
        g.logger.debug(
            f"Request - Method: {request.method}, Path: {request.path}, "
            f"Query Parameters: {request.args}, Data: {request.data.decode()}, "
            f"Headers: {request.headers}"
        )

        g.stocks_cache.clear()
        portfolio: List[Stock] = get_portfolio_data()
        watch_list = load_watchlist()
        g.logger.debug("watch list is {}".format(watch_list))
        try:
            yahoo_data = YahooRequestor().request(
                set().union(map(lambda s: s.symbol, portfolio), watch_list)
            )
            for stock in portfolio:
                try:
                    stock.set_api_data(
                        next(filter(lambda s: s["symbol"] == stock.symbol, yahoo_data))
                    )  # expect only 1
                except StopIteration:
                    g.logger.warning("API data not found for {}".format(stock))
                g.stocks_cache.append(stock)
            for watch_stock in watch_list:
                api_data = next(
                    filter(lambda s: s["symbol"] == watch_stock, yahoo_data), None
                )  # expect only 1
                if api_data:
                    stock = Stock(
                        {
                            "Symbol": api_data["symbol"],
                            "Day's Value": round(
                                api_data.get(
                                    get_market_state_key(api_data.get("marketState"))
                                    + "MarketChange",
                                    0,
                                ),
                                2,
                            ),
                            "Entry Type": "W",
                            "Last": api_data.get(
                                get_market_state_key(api_data.get("marketState"))
                                + "MarketPrice",
                                api_data.get("regularMarketPrice", -1),
                            ),
                            "Change": api_data.get(
                                get_market_state_key(api_data.get("marketState"))
                                + "MarketChange",
                                0,
                            ),
                        }
                    )
                    stock.set_api_data(api_data)
                    g.stocks_cache.append(stock)
                else:
                    g.logger.warning(
                        "could not find watchlist entry for {}".format(watch_stock)
                    )
        except ConnectionError as e:
            g.logger.error("connection Error while getting API", e)
            abort(http.HTTPStatus.INTERNAL_SERVER_ERROR.value)

        return g.stocks_cache


@app.route("/ticker/<name>")
@require_authentication
def ticker_data(name: str) -> Dict[str, Any]:
    return {
        "stock": next(filter(lambda x: x.symbol == name, g.stocks_cache)),
        "market-state-4calc": get_market_state_key(
            g.stocks_cache[0].api_data.get("marketState", "")
        ),
    }


def get_portfolio_data() -> List[Stock]:
    stocks: List[Stock] = list()
    try:
        df = pd.read_html(io.StringIO(get_portfolio_table()))[0]

        required_columns = [
            "Symbol",
            "Qty",
            "Change",
            "Last",
            "Day's Value",
            "Average Cost",
            "Gain",
            "Profit/ Loss",
            "Value",
        ]
        optional_columns = ["Entry Type", "Expiration", "Strike", "Put/ Call"]
        existing_columns = required_columns + [
            col for col in optional_columns if col in df.columns
        ]

        data = json.loads(df[existing_columns].to_json(orient="records"))
        total_val = 0.0
        for d in data:
            s = Stock(d)
            stocks.append(s)
            total_val += s.total_val
        for s in stocks:
            s.set_weight(total_val)
    except Exception:
        g.logger.exception("failed to get portfolio data")
        data = []
    g.logger.debug("portfolio symbols: {}".format([sub["Symbol"] for sub in data]))
    return stocks


@app.route("/js/<path:path>")
def send_js(path: str) -> Response:
    return send_from_directory("static/js", path)


@app.route("/css/<path:path>")
def send_css(path: str) -> Response:
    return send_from_directory("static/css", path)


@app.route("/webfonts/<path:path>")
def send_webfonts(path: str) -> Response:
    return send_from_directory("static/webfonts", path)


@app.route("/favicon/<path:icon>")
def favicon(icon: str) -> Response:
    if icon == "site.webmanifest":
        return send_from_directory("static/favicon", icon)
    else:
        return send_from_directory("static/favicon", icon, mimetype="image/x-icon")


@app.route("/")
def root() -> Response:
    if auth_utils.is_authenticated():
        return app.send_static_file("index.html")
    else:
        return app.send_static_file("401.html")


@app.route("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.route("/watchList", methods=["GET"])
def get_strings() -> List[str]:
    return list(load_watchlist())


def load_watchlist() -> Set[str]:
    return set(g.config.get("watch_list", list()))


@app.route("/watchList", methods=["POST"])
def update_watchlist() -> tuple[Response, int]:
    with g.config_lock:
        new_watchlist = request.json
        if not isinstance(new_watchlist, list):
            g.logger.error("invalid request for update_watchlist")
            return jsonify({"error": "'watchlist' should be a list"}), 400

        g.config.set("watch_list", new_watchlist)
        g.config.save()

    return jsonify({"message": "Watchlist updated successfully"}), 200


def main() -> None:
    logging.basicConfig(stream=sys.stdout)
    g.logger = logging.getLogger("waitress")
    g.logger.setLevel(os.getenv("APP_LOG_LEVEL", logging.INFO))
    g.config = Config()
    g.time_format = g.config.get("time_format")
    g.persist = TrendPersist(g.trends)
    g.logger.info("starting meitav-view app")
    g.trends = g.persist.load()

    serve(
        app,
        listen="*:{}".format(os.getenv("APP_PORT", 8080)),
        url_prefix=os.getenv("URL_PREFIX", ""),
        threads=2,
    )


if __name__ == "__main__":
    main()
