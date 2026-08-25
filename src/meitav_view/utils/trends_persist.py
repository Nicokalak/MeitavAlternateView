"""Trend History Manager for Stock Portfolio Viewer.

Persists chart trend data to a JSON file and prunes entries older than 36 hours.
Stores trends as a dict with keys 'PRE_histo', 'REGULAR_histo', 'POST_histo',
each mapping date-string keys to float values.

All public methods are thread-safe via copy-on-write snapshots (no locks).
"""

import copy
import json
import os
import threading
from datetime import datetime, timedelta
from typing import Any

from meitav_view.model.config import Config
from meitav_view.model.stock import Stock

_STALE_THRESHOLD = timedelta(days=1, seconds=43200)


class TrendPersist:
    """Manage trend history with thread-safe copy-on-write operations.

    Trends dict structure: ``{'PRE_histo': {date_str: float, ...}, ...}``

    Thread safety is achieved by building new dicts and atomically reassigning
    ``self.trends``, avoiding iteration-during-mutation races under free-threading.
    """

    _DEFAULT_PERSIST_FILE = "meitav_trends.json"

    def __init__(self, config: Config, trends: dict[str, Any] | None = None):
        self.trends = trends if trends else {"PRE_histo": {}, "REGULAR_histo": {}, "POST_histo": {}}
        self.config = config

    @property
    def _persist_path(self) -> str:
        return os.environ.get("PERSIST_FILE", self._DEFAULT_PERSIST_FILE)

    def save(self) -> None:
        """Snapshot trends and write to disk in a background daemon thread."""
        snapshot = copy.deepcopy(self.trends)
        t = threading.Thread(target=self._save_snapshot, args=(snapshot,), daemon=True)
        t.start()

    def _save_snapshot(self, snapshot: dict[str, Any]) -> None:
        with open(self._persist_path, "w") as f:
            json.dump(snapshot, f, indent=4)

    def load(self) -> "TrendPersist":
        if os.path.exists(self._persist_path):
            with open(self._persist_path) as f:
                self.trends = json.load(f)
        return self

    def get_trends(self) -> dict[str, Any]:
        """Return a deep copy of trends so callers never race with mutations."""
        return copy.deepcopy(self.trends)

    def trends_for_chart(self, state_histo_key: str, histo_val: float) -> None:
        """Prune stale entries and record a new data point — copy-on-write.

        Builds a brand-new ``trends`` dict with old entries filtered out and
        the new value inserted, then atomically reassigns ``self.trends``.
        No iteration-during-mutation is possible.
        """
        now = datetime.now()
        time_fmt = self.config.time_format()

        new_trends = {
            key: {
                date: val
                for date, val in histo.items()
                if (now - datetime.strptime(date, time_fmt)) <= _STALE_THRESHOLD
            }
            for key, histo in self.trends.items()
        }
        new_trends[state_histo_key][now.strftime(time_fmt)] = histo_val
        self.trends = new_trends

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
