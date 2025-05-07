import logging
from typing import List, Set

from curl_cffi import requests

logger = logging.getLogger()


class YahooRequestor(object):
    API = 'https://query2.finance.yahoo.com/v7/finance/quote?crumb={}&symbols={}'

    def __init__(self, symbols: Set[str]):
        self.symbols = symbols
        self.session = requests.Session(impersonate="chrome")
        r1 = self.session.get("https://query2.finance.yahoo.com/v1/test/getcrumb")
        self._crumb = r1.text

    def request(self):
        url = "https://query2.finance.yahoo.com/v7/finance/quote"
        params = {"symbols": ",".join(self.symbols),
                  "crumb": self._crumb, }
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("quoteResponse", {}).get("result", [])
        else:
            logger.error(response)
            return []

