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
        return set(self.config.get("watch_list", []))

    def get_trends(self) -> dict[str, Any]:
        return self.trends_persist.get_trends()

    def enrich_portfolio(self) -> list[Stock]:
        """Enrich the portfolio with the api data"""
        portfolio: list[Stock] = self.get_portfolio_data()
        self.logger.debug(f"watch list is {self.watchlist}")
        yahoo_data = self.yahoo_requestor.request(
            set().union((s.symbol for s in portfolio), self.watchlist),
        )
        for stock in portfolio:
            try:
                stock.set_api_data(
                    next(filter(lambda s: s["symbol"] == stock.symbol, yahoo_data)),
                )  # expect only 1
            except StopIteration:
                self.logger.warning(f"API data not found for {stock}")

        for watch_stock in self.watchlist:
            api_data = next(
                filter(lambda s: s["symbol"] == watch_stock, yahoo_data),
                None,
            )  # expect only 1
            if api_data:
                stock = Stock(
                    {
                        "Symbol": api_data["symbol"],
                        "Day's Value": round(
                            api_data.get(
                                self._get_market_state_key(api_data.get("marketState")) + "MarketChange",
                                0,
                            ),
                            2,
                        ),
                        "Entry Type": "W",
                        "Last": api_data.get(
                            self._get_market_state_key(api_data.get("marketState")) + "MarketPrice",
                            api_data.get("regularMarketPrice", -1),
                        ),
                        "Change": api_data.get(
                            self._get_market_state_key(api_data.get("marketState")) + "MarketChange",
                            0,
                        ),
                    },
                )
                stock.set_api_data(api_data)
                portfolio.append(stock)
            else:
                self.logger.warning(f"could not find watchlist entry for {watch_stock}")

        self._stocks = portfolio
        return self._stocks

    @staticmethod
    def _get_market_state_key(market_state: str = "post") -> str:
        return market_state.lower() if market_state.lower() in ("pre", "post", "regular") else "post"

    def get_current_market_state_key(self) -> str:
        return self._get_market_state_key(
            next(self._stocks.__iter__()).api_data.get("marketState", ""),
        )

    def get_market_state(self) -> dict[str, Any]:
        if len(self._stocks) == 0:
            raise RuntimeError("no stocks found")

        result = {
            "marketState": self._stocks[0].api_data.get("marketState"),
            "trend": 0,
            "yahoo_trend": 0,
        }
        change = MeitavViewer._get_market_state_key(self._stocks[0].api_data.get("marketState", "")) + "MarketChange"
        change_per = (
            MeitavViewer._get_market_state_key(self._stocks[0].api_data.get("marketState", "")) + "MarketChangePercent"
        )
        self.trends_persist.add_trend(self._stocks, result, change)
        result["top-gainer"] = max(self._stocks, key=lambda s: s.api_data.get(change, 0) * s.quantity)
        result["top-gainer%"] = max(self._stocks, key=lambda s: s.api_data.get(change_per, 0))
        result["top-loser"] = min(self._stocks, key=lambda s: s.api_data.get(change, 0) * s.quantity)
        result["top-loser%"] = min(self._stocks, key=lambda s: s.api_data.get(change_per, 0))
        result["top-mover"] = max(
            self._stocks,
            key=lambda s: s.api_data.get("regularMarketVolume", 0),
        )
        result["up-down"] = {
            "up": len(list(filter(lambda sd: sd.gain is not None and sd.gain > 0, self._stocks))),
            "down": len(list(filter(lambda sd: sd.gain is not None and sd.gain < 0, self._stocks))),
        }
        result["trending"] = max(
            self._stocks,
            key=lambda s: s.api_data.get("regularMarketVolume", 0)
            / s.api_data.get("averageDailyVolume10Day", sys.maxsize),
        )

        return result

    def find_stock(self, name: str) -> Stock | None:
        return next(filter(lambda x: x.symbol == name, self._stocks))
