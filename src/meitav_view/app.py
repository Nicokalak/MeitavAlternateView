import http
import logging
import os
import sys
import threading
from http import HTTPStatus
from typing import Any, ClassVar, Dict, List, Set

from flask import Flask, Response, abort, jsonify, request, send_from_directory
from waitress import serve

from meitav_view.model.config import Config
from meitav_view.model.stock import Stock
from meitav_view.utils import auth_utils
from meitav_view.utils.auth_utils import require_authentication
from meitav_view.utils.trends_persist import TrendPersist
from meitav_view.utils.yahoo_requestor import YahooRequestor
from meitav_view.viewer import MeitavViewer


class AppGlobs:
    stocks_cache: ClassVar[List[Stock]] = list()
    lock = threading.Lock()
    config: Config
    logger: logging.Logger
    trends: TrendPersist
    viewer: MeitavViewer


app = Flask(__name__, static_url_path="/static/")
g = AppGlobs()


@app.route("/trends")
@require_authentication
def get_trends() -> Dict[str, Any]:
    return g.trends.get_trends()


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
    g.trends.add_trend(g.stocks_cache, result, change)
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
        portfolio: List[Stock] = g.viewer.get_portfolio_data()
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
        except ConnectionError:
            g.logger.exception("connection Error while getting API")
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
def get_watchlist() -> List[str]:
    return list(load_watchlist())


def load_watchlist() -> Set[str]:
    return set(g.config.get("watch_list", list()))


@app.route("/watchList", methods=["POST"])
def update_watchlist() -> tuple[Response, int]:
    new_watchlist = request.json
    if not isinstance(new_watchlist, list):
        g.logger.error("invalid request for update_watchlist")
        return jsonify(
            {"error": "'watchlist' should be a list"}
        ), HTTPStatus.BAD_REQUEST

    g.config.set_and_save("watch_list", new_watchlist)

    return jsonify({"message": "Watchlist updated successfully"}), HTTPStatus.OK


def main() -> None:
    logging.basicConfig(stream=sys.stdout)
    g.logger = logging.getLogger("waitress")
    g.logger.setLevel(os.getenv("APP_LOG_LEVEL", logging.INFO))
    g.config = Config()
    g.trends = TrendPersist(g.config)
    g.trends.load()
    g.logger.info("starting meitav-view app")
    g.viewer = MeitavViewer(config=g.config)

    serve(
        app,
        listen="*:{}".format(os.getenv("APP_PORT", "8080")),
        url_prefix=os.getenv("URL_PREFIX", ""),
        threads=2,
    )


if __name__ == "__main__":
    main()
