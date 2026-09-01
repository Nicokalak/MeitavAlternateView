import http
import io
import json
import logging
import os
import sys
from typing import Any

import pandas as pd
import requests

from meitav_view.model.config import Config
from meitav_view.model.stock import Stock
from meitav_view.model.watchlist import WatchlistItem
from meitav_view.utils.trends_persist import TrendPersist
from meitav_view.utils.yahoo_requestor import YahooRequestor


class MeitavViewer:
    PORTFOLIO_URL_FILE = "MEITAV_PORTFOLIO_URL_FILE"

    def __init__(self) -> None:
        self.config = Config()
        self.trends_persist = TrendPersist(self.config).load()
        self.url = self._get_url()
        self.logger = logging.getLogger(MeitavViewer.__name__)
        self._stocks: list[Stock] = []
        self.yahoo_requestor = YahooRequestor()

    def _get_url(self) -> str:
        if self.PORTFOLIO_URL_FILE in os.environ:
            try:
                with open(os.environ[self.PORTFOLIO_URL_FILE]) as f:
                    return f.read().strip()
            except FileNotFoundError:
                self.logger.error(f"{os.environ[self.PORTFOLIO_URL_FILE]} secret not found")

        return os.getenv("portfolio_link", "")

    def get_portfolio_table(self) -> str | None:
        try:
            attempts = 0
            r = requests.get(
                self.url,
                timeout=self.config.request_timeout(),
                headers={"User-Agent": "Meitav-Viewer/{}".format(os.getenv("HOSTNAME"))},
            )
            while attempts < self.config.get("retry_attempts", 3) and r.status_code != http.HTTPStatus.OK.value:
                attempts += 1
                self.logger.error(
                    f"failed to get portfolio from Meitav attempt {attempts} stats {r.status_code} {r.text}",
                )
                r = requests.get(
                    self.url,
                    timeout=self.config.request_timeout(),
                    headers={"User-Agent": "Meitav-Viewer/{}".format(os.getenv("HOSTNAME"))},
                )
            return r.text
        except ConnectionError:
            self.logger.exception("failed to connect to meitav")
            return None

    def get_portfolio_data(self) -> list[Stock]:
        stocks: list[Stock] = []
        try:
            df = pd.read_html(io.StringIO(self.get_portfolio_table()))[0]

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
            existing_columns = required_columns + [col for col in optional_columns if col in df.columns]

            data = json.loads(df[existing_columns].to_json(orient="records"))
            total_val = 0.0
            for d in data:
                s = Stock(d)
                stocks.append(s)
                total_val += s.total_val
            for s in stocks:
                s.set_weight(total_val)

            self.logger.debug("portfolio symbols: {}".format([sub["Symbol"] for sub in data]))
        except Exception:
            self.logger.exception("failed to get portfolio data")
        return stocks

    @property
    def watchlist(self) -> set[str]:
        return {item.symbol for item in self.get_watchlist_items()}

    def get_watchlist_items(self) -> list[WatchlistItem]:
        raw_list = self.config.get("watch_list", [])
        items: list[WatchlistItem] = []
        for entry in raw_list:
            try:
                items.append(WatchlistItem.from_entry(entry))
            except Exception:
                self.logger.warning(f"Failed to parse watchlist entry: {entry}")
        return items

    def save_watchlist(self, items: list[WatchlistItem]) -> None:
        serialized = [item.model_dump(by_alias=False) for item in items]
        self.config.set_and_save("watch_list", serialized)

    def get_trends(self) -> dict[str, Any]:
        return self.trends_persist.get_trends()

    def enrich_portfolio(self) -> list[Stock]:
        """Enrich the portfolio with the api data"""
        portfolio: list[Stock] = self.get_portfolio_data()
        watchlist_items = self.get_watchlist_items()
        self.logger.debug(f"watch list is {[item.symbol for item in watchlist_items]}")
        yahoo_data = self.yahoo_requestor.request(
            set().union((s.symbol for s in portfolio), (item.symbol for item in watchlist_items)),
        )
        for stock in portfolio:
            try:
                stock.set_api_data(
                    next(filter(lambda s: s["symbol"] == stock.symbol, yahoo_data)),
                )  # expect only 1
            except StopIteration:
                self.logger.warning(f"API data not found for {stock}")

        for watch_item in watchlist_items:
            api_data = next(
                filter(lambda s: s["symbol"] == watch_item.symbol, yahoo_data),
                None,
            )  # expect only 1
            if api_data:
                market_key = self._get_market_state_key(api_data.get("marketState"))
                last_price = float(
                    api_data.get(
                        market_key + "MarketPrice",
                        api_data.get("regularMarketPrice", -1),
                    )
                )
                market_change = float(
                    api_data.get(
                        market_key + "MarketChange",
                        0,
                    )
                )
                qty = watch_item.quantity
                cost = watch_item.cost

                day_val = round(market_change * qty, 2) if qty > 0 else round(market_change, 2)
                total_val = round(last_price * qty, 2) if qty > 0 and last_price > 0 else 0.0
                total_change = round((last_price - cost) * qty, 2) if qty > 0 and cost > 0 and last_price > 0 else 0.0
                gain = round(((last_price - cost) / cost) * 100, 2) if cost > 0 and last_price > 0 else 0.0

                stock_dict = {
                    "Symbol": api_data["symbol"],
                    "Day's Value": day_val,
                    "Entry Type": "W",
                    "Last": last_price,
                    "Change": market_change,
                    "Qty": qty,
                    "Average Cost": cost if cost > 0 else None,
                    "Value": total_val,
                    "Profit/ Loss": total_change,
                    "Gain": gain,
                }
                stock = Stock(stock_dict)
                stock.set_api_data(api_data)
                portfolio.append(stock)
            else:
                self.logger.warning(f"could not find watchlist entry for {watch_item.symbol}")

        self._stocks = portfolio
        return self._stocks

    @staticmethod
    def _get_market_state_key(market_state: str = "post") -> str:
        return market_state.lower() if market_state.lower() in ("pre", "post", "regular") else "post"

    def get_current_market_state_key(self) -> str:
        stocks = self._stocks
        if not stocks:
            return "post"
        market_state = next(
            (s.api_data.get("marketState", "") for s in stocks if s.api_data and s.api_data.get("marketState")),
            "",
        )
        return self._get_market_state_key(market_state)

    def get_market_state(self) -> dict[str, Any]:
        stocks = self._stocks
        if len(stocks) == 0:
            raise RuntimeError("no stocks found")

        market_state = next(
            (s.api_data.get("marketState") for s in stocks if s.api_data and s.api_data.get("marketState")),
            None,
        )
        result = {
            "marketState": market_state,
            "trend": 0,
            "yahoo_trend": 0,
        }
        change = MeitavViewer._get_market_state_key(market_state or "") + "MarketChange"
        change_per = MeitavViewer._get_market_state_key(market_state or "") + "MarketChangePercent"
        self.trends_persist.add_trend(stocks, result, change)
        result["top-gainer"] = max(stocks, key=lambda s: s.api_data.get(change, 0) * s.quantity)
        result["top-gainer%"] = max(stocks, key=lambda s: s.api_data.get(change_per, 0))
        result["top-loser"] = min(stocks, key=lambda s: s.api_data.get(change, 0) * s.quantity)
        result["top-loser%"] = min(stocks, key=lambda s: s.api_data.get(change_per, 0))
        result["top-mover"] = max(
            stocks,
            key=lambda s: s.api_data.get("regularMarketVolume", 0),
        )
        result["up-down"] = {
            "up": len(list(filter(lambda sd: sd.gain is not None and sd.gain > 0, stocks))),
            "down": len(list(filter(lambda sd: sd.gain is not None and sd.gain < 0, stocks))),
        }
        result["trending"] = max(
            stocks,
            key=lambda s: (
                s.api_data.get("regularMarketVolume", 0) / s.api_data.get("averageDailyVolume10Day", sys.maxsize)
            ),
        )

        return result

    def find_stock(self, name: str) -> Stock | None:
        stocks = self._stocks
        return next((x for x in stocks if x.symbol == name), None)
