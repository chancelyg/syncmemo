import logging
import os

from yaml import safe_load
from diskcache import Cache
import threading

CONST_VERSION = "V2.0"


def load_yaml(file_path):
    with open(file_path, "r") as f:
        return safe_load(f)


config = load_yaml(os.environ["CONFIG"])


class Response:
    def __init__(self, status: int, msg: str, data: dict = {}):
        super().__init__()
        self.status = status
        self.msg = msg
        self.data = data
        self.version = config["system"]["version"]


class Memo:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Memo, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, disk_cache_dir, expire=0):
        if self._initialized:
            return
        self.disk_cache = Cache(disk_cache_dir)
        self.expire = expire
        self._initialized = True
        self.flask_cache = None

    def set(self, key, value):
        if self.expire != 0:
            self.disk_cache.set(key, value, expire=self.expire)
        if self.expire == 0:
            self.disk_cache.set(key, value)

    def get(self, key):
        value = self.disk_cache.get(key)
        if value is not None:
            return value

        # If not found in both, initialize with empty string in DiskCache
        self.disk_cache.set(key, "", expire=self.expire)
        return ""


class Logger(logging.Logger):
    def __init__(self) -> None:
        super().__init__(name="syncmemo")
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.addHandler(stream_handler)


logger = Logger()
