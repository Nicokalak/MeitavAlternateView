import json
import logging
import os
import threading
from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
class Config:
    DEFAULT_CONFIG_FILE = "/app/config.json"
    DEFAULT_TIME_FORMAT = "%Y%m%dT%H:%M:%S"
    CONFIG_LOCK = threading.Lock()
    DEFAULT_REQUEST_TIMEOUT = 30

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._settings: dict[str, Any] = {}
        self._load_config()

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def _load_config(self) -> None:
        with open(os.getenv("DEFAULT_CONF", self.DEFAULT_CONFIG_FILE)) as config_file:
            self._settings = json.load(config_file)
            config_file.close()

    def time_format(self) -> str:
        return str(self._settings.get("time_format", self.DEFAULT_TIME_FORMAT))

    def save(self) -> None:
        with open(os.getenv("DEFAULT_CONF", self.DEFAULT_CONFIG_FILE), "w") as config_file:
            self.logger.info("saved new configurations")
            json.dump(self._settings, config_file, indent=4)

    def set_and_save(self, key: str, value: Any) -> None:
        with self.CONFIG_LOCK:
            self._settings[key] = value
            self.save()

    def request_timeout(self) -> float:
        return float(self.get("request_timeout", self.DEFAULT_REQUEST_TIMEOUT))
