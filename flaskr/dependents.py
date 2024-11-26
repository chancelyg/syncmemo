import os

from yaml import safe_load
from diskcache import Cache


def load_yaml(file_path):
    with open(file_path, "r") as f:
        return safe_load(f)


config = load_yaml(os.environ["CONFIG"])

cache = Cache(config["system"]["cache"])

CONST_VERSION = "V2.0"


class Response:
    def __init__(self, status: int, msg: str, data: dict = {}):
        super().__init__()
        self.status = status
        self.msg = msg
        self.data = data
        self.version = config["system"]["version"]
