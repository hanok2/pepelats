import logging
import os
import sys
from json import dump, load
from pathlib import Path
from typing import Any, Dict, Union
from typing import List

import mido

from utils._utilsother import ConfigName, ROOT_DIR


# noinspection PyUnresolvedReferences
def open_midi_ports():
    port_names_str: str = os.getenv(ConfigName.midi_port_names)
    try:
        port_names: List[str] = json.loads("[" + port_names_str + "]")
    except Exception as ex:
        logging.error(f"Failed to parse {ConfigName.midi_port_names} error: {ex}\nstring value: {port_names_str}")
        sys.exit(1)

    logging.info("Waiting for MIDI port to appear:", port_names)
    port_list = mido.get_input_names()
    for name in port_names:
        for port_name in port_list:
            if name in port_name:
                print("opening:", port_name)
                port_in = mido.open_input(port_name)
                return port_in


class JsonDictLoader:
    def __init__(self, filename: Union[str, Path]):
        self.__filename = Path(ROOT_DIR, filename)
        self.__filename.parent.mkdir(parents=True, exist_ok=True)
        self.__app_dict: Dict[str, Any] = dict()

        with open(self.__filename) as f:
            self.__app_dict = load(f)

        if not isinstance(self.__app_dict, dict):
            raise RuntimeError("JSON file must have dictionary {self.__filename}")
        if len(self.__app_dict) == 0:
            raise RuntimeError("JSON file must have non empty dictionary {self.__filename}")

    def save(self) -> None:
        with open(self.__filename, "w") as f:
            dump(self.__app_dict, f, indent=2)

    def set(self, key: str, value: Any) -> None:
        self.__app_dict[key] = value

    def get(self, key: str, default) -> Any:
        return self.__app_dict.get(key, default)

    def add_if_missing(self, key: str, default) -> None:
        if key not in self.__app_dict:
            self.__app_dict[key] = default

    def get_keys(self) -> List[str]:
        return [*self.__app_dict]

    def get_filename(self):
        return self.__filename


class MainLoader:
    """class will only static methods to keep app's main configs"""
    __dl = JsonDictLoader("etc/looper_defaults.json")

    @staticmethod
    def get(key: str, default) -> Any:
        return MainLoader.__dl.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        return MainLoader.__dl.set(key, value)

    @staticmethod
    def save() -> None:
        return MainLoader.__dl.save()

    @staticmethod
    def _make_content():
        """This is not used, just for info"""
        MainLoader.__dl.add_if_missing(ConfigName.drum_swing, 0.75)
        MainLoader.__dl.add_if_missing(ConfigName.drum_volume, 0.3)
        MainLoader.__dl.add_if_missing(ConfigName.drum_type, "pop")


if __name__ == "__main__":
    pass
