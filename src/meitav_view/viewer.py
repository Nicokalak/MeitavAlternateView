import http
import io
import json
import logging
import os
from typing import List, Optional

import pandas as pd
import requests

from meitav_view.model.config import Config
from meitav_view.model.stock import Stock


class MeitavViewer:
    def __init__(self, config: Config):
        self.config = config
        self.url = os.getenv("portfolio_link", "")
        self.logger = logging.getLogger(MeitavViewer.__name__)

    def get_portfolio_table(self) -> Optional[str]:
        try:
            attempts = 0
            r = requests.get(
                self.url,
                headers={"User-Agent": "Meitav-Viewer/{}".format(os.getenv("HOSTNAME"))},
            )
            while (
                attempts < self.config.get("retry_attempts", 3)
                and r.status_code != http.HTTPStatus.OK.value
            ):
                attempts += 1
                self.logger.error(
                    "failed to get portfolio from Meitav attempt {} stats {} {}".format(
                        attempts, r.status_code, r.text
                    )
                )
                r = requests.get(
                    self.url,
                    headers={"User-Agent": "Meitav-Viewer/{}".format(os.getenv("HOSTNAME"))},
                )
            return r.text
        except ConnectionError:
            self.logger.exception("failed to connect to meitav")
            return None

    def get_portfolio_data(self) -> List[Stock]:
        stocks: List[Stock] = list()
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
            self.logger.exception("failed to get portfolio data")
            data = []
        self.logger.debug("portfolio symbols: {}".format([sub["Symbol"] for sub in data]))
        return stocks
