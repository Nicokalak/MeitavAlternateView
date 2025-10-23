import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any

from meitav_view.model.config import Config
from meitav_view.model.stock import Stock


class TrendPersist:
    _DEFAULT_PERSIST_FILE = "meitav_trends.json"

    def __init__(self, config: Config, trends: dict[str, Any] | None = None):
        self.trends = trends if trends else {"PRE_histo": {}, "REGULAR_histo": {}, "POST_histo": {}}
        self.config = config
        self._exec = ThreadPoolExecutor(max_workers=1)

    def save(self) -> None:
        self._exec.submit(self.__save_to_file)

    def __save_to_file(self) -> None:
        with open(os.environ.get("PERSIST_FILE", self._DEFAULT_PERSIST_FILE), "w") as write_file:
            json.dump(self.trends, write_file, indent=4)

    def load(self) -> "TrendPersist":
        if os.path.exists(os.environ.get("PERSIST_FILE", self._DEFAULT_PERSIST_FILE)):
            with open(os.environ.get("PERSIST_FILE", self._DEFAULT_PERSIST_FILE)) as load_file:
                self.trends = json.load(load_file)
        return self

    def get_trends(self) -> dict[str, Any]:
        return self.trends

    def trends_for_chart(self, state_histo_key: str, histo_val: float) -> None:
        curr_histo = self.trends[state_histo_key]

        to_delete = []
        for key, state_histo in self.trends.items():
            for date in state_histo.keys():
                if (datetime.now() - datetime.strptime(date, self.config.time_format())) > timedelta(
                    days=1,
                    seconds=43200,
                ):
                    to_delete.append((key, date))
        for tup in to_delete:
            del self.trends[tup[0]][tup[1]]

        curr_histo[datetime.now().strftime(self.config.time_format())] = histo_val

    def add_trend(
        self,
        stocks_cache: list[Stock],
        trends_obj: dict[str, Any],
        change_key: str,
    ) -> None:
        trends_obj["trend"] = 0
        trends_obj["watchlist_trend"] = 0
        m_state = trends_obj["marketState"]
        state_histo = m_state + "_histo"
        watchlist_sum = 0.0
        watchlist_count = 0.0
        if m_state in ("CLOSED", "PREPRE", "POSTPOST"):
            return
        for s in stocks_cache:
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
        self.trends_for_chart(state_histo, trends_obj["yahoo_trend"])
        self.save()
