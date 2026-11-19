"""Persist and prune chart trend history (PRE / REGULAR / POST histograms)."""

import copy
import json
import os
import threading
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, ClassVar

from meitav_view.model.config import Config
from meitav_view.model.stock import Stock

_STALE_THRESHOLD = timedelta(days=1, seconds=43200)


@lru_cache(maxsize=64)
def _parse_dt(date_str: str, fmt: str) -> datetime:
    """Cache parsed timestamps to avoid redundant strptime calls."""
    return datetime.strptime(date_str, fmt)


class TrendPersist:
    """Thread-safe copy-on-write trend history manager."""

    _DEFAULT_PERSIST_FILE = "meitav_trends.json"

    def __init__(self, config: Config, trends: dict[str, Any] | None = None):
        self.trends = trends if trends else {"PRE_histo": {}, "REGULAR_histo": {}, "POST_histo": {}}
        self.config = config

    @property
    def _persist_path(self) -> str:
        return os.environ.get("PERSIST_FILE", self._DEFAULT_PERSIST_FILE)

    def save(self) -> None:
        """Write a snapshot of trends to disk in a background thread."""
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
        """Return a deep copy of trends to avoid mutation races."""
        return copy.deepcopy(self.trends)

    # On session transition, clear histograms from prior sessions.
    _SESSION_PREDECESSORS: ClassVar[dict[str, tuple[str, ...]]] = {
        "PRE_histo": ("REGULAR_histo", "POST_histo"),
        "REGULAR_histo": ("POST_histo",),
        "POST_histo": (),
    }

    def trends_for_chart(self, state_histo_key: str, histo_val: float) -> None:
        """Prune stale entries, clear prior sessions, and record a new data point."""
        now = datetime.now()
        time_fmt = self.config.time_format()
        clear_keys = self._SESSION_PREDECESSORS.get(state_histo_key, ())

        new_trends = {
            key: (
                {}
                if key in clear_keys
                else {
                    date: val
                    for date, val in histo.items()
                    if (now - _parse_dt(date, time_fmt)) <= _STALE_THRESHOLD
                }
            )
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
