from typing import Literal, Any, Dict, List
import json


class _Debugger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_Debugger, cls).__new__(cls)
            cls._instance.mode = "off"
            cls._instance._data = {}
        return cls._instance

    @property
    def data(self) -> Dict[str, List[Any]]:
        if self.mode == "on":
            return self._data
        else:
            return {}

    @data.setter
    def data(self, value):
        if self.mode == "on":
            self._data = value
        else:
            self._data = {}

    def push(self, name_space: str, content: Any):
        if self.mode == "on":
            if name_space not in self.data.keys():
                self.data[name_space] = []
            self.data[name_space].append(content)

    def set_mode(self, mode: Literal["on", "off"]):
        self.mode = mode
        if mode == "off":
            self._data = {}


def pretty_json(data):
    print(json.dumps(data, indent=2))


Debugger = _Debugger()
