import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict


class TrendPersist(object):
    def __init__(self, trends: Dict):
        super(TrendPersist).__init__()
        self.trends = trends
        self._exec = ThreadPoolExecutor(max_workers=1)

    def save(self):
        self._exec.submit(self.__save_to_file)

    def __save_to_file(self):
        with open(os.environ.get("PERSIST_FILE", "/tmp/meitav_trends.json"), "w") as write_file:
            json.dump(self.trends, write_file, indent=4)

    def load(self):
        if os.path.exists(os.environ.get("PERSIST_FILE", "/tmp/meitav_trends.json")):
            with open(os.environ.get("PERSIST_FILE", "/tmp/meitav_trends.json"), "r") as loadFile:
                self.trends = json.load(loadFile)
        return self.trends
