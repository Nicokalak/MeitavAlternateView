import logging
from functools import lru_cache
from typing import Any, Set

from curl_cffi import Session, requests

logger = logging.getLogger()


@lru_cache(maxsize=1)
class YahooRequestor:
    API = "https://query2.finance.yahoo.com/v7/finance/quote?crumb={}&symbols={}"

    def __init__(self) -> None:
        self.session: Session[Any] = requests.Session(impersonate="chrome")
        r1 = self.session.get("https://query2.finance.yahoo.com/v1/test/getcrumb")
        self._crumb = r1.text

    def request(self, symbols: Set[str]) -> Any:
        url = "https://query2.finance.yahoo.com/v7/finance/quote"
        params = {
            "symbols": ",".join(symbols),
            "crumb": self._crumb,
        }
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("quoteResponse", {}).get("result", [])
        else:
            logger.error(response)
            return []
