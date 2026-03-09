import json
import os


class Config:

    DB_CONNECTION_STRING: str = "sqlite:///:memory:"

    __instances: dict[str, Config] = {}

    def __init__(self, file_name: str = ""):
        if str in Config.__instances:
            raise RuntimeError("Don't Call constructor!")
        Config.__instances[file_name] = self
        if file_name:
            self._load(file_name)
        else:
            self._connection_string: str = Config.DB_CONNECTION_STRING

    def _load(self, filename: str) -> None:
        if os.path.isfile(filename):
            with open(filename, "r") as f:
                self._connection_string = json.load(f)["connection_string"]

    @property
    def connection_string(self) -> str:
        return self._connection_string

    @classmethod
    def get_instance(cls, file_name: str = "") -> Config:
        if file_name in cls.__instances:
            return cls.__instances[file_name]
        return Config(file_name)
