import logging
from functools import cached_property, lru_cache
from http import HTTPStatus
from typing import Any

from curl_cffi import Session, requests

logger = logging.getLogger()


@lru_cache(maxsize=1)
class YahooRequestor:
    API = "https://query2.finance.yahoo.com/v7/finance/quote?crumb={}&symbols={}"

    def __init__(self) -> None:
        self.session: Session[Any] = requests.Session(impersonate="chrome")
        # Crumb is no longer fetched here on startup

    @cached_property
    def crumb(self) -> str:
        """Fetches the crumb lazily on first access and caches the result."""
        response = self.session.get("https://query2.finance.yahoo.com/v1/test/getcrumb")
        return response.text

    def request(self, symbols: set[str]) -> Any:
        url = "https://query2.finance.yahoo.com/v7/finance/quote"
        params = {
            "symbols": ",".join(symbols),
            "crumb": self.crumb,
        }
        response = self.session.get(url, params=params)
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            return data.get("quoteResponse", {}).get("result", [])
        logger.error(response)
        return []
