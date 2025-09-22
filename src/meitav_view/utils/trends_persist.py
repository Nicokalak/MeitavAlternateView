import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict


class TrendPersist(object):
    def __init__(self, trends: Dict[str, Any]):
        self.trends = trends
        self._exec = ThreadPoolExecutor(max_workers=1)

    def save(self) -> None:
        self._exec.submit(self.__save_to_file)

    def __save_to_file(self) -> None:
        with open(
            os.environ.get("PERSIST_FILE", "/tmp/meitav_trends.json"), "w"
        ) as write_file:
            json.dump(self.trends, write_file, indent=4)

    def load(self) -> Dict[str, Any]:
        if os.path.exists(os.environ.get("PERSIST_FILE", "/tmp/meitav_trends.json")):
            with open(
                os.environ.get("PERSIST_FILE", "/tmp/meitav_trends.json"), "r"
            ) as load_file:
                self.trends = json.load(load_file)
        return self.trends
