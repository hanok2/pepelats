from json import load, dump
from pathlib import Path
from typing import Any, List, Dict, Union

from utils._utilsother import ROOT_DIR, ConfigName


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

    def get_dict(self, merge_name: str) -> Dict[str, Dict]:
        """get Dict[str, Dict] where merge name is the default sub dictionary.
       Every sub dictionary is merged with the default"""
        merge_dict = self.get(merge_name, dict())
        result = dict()
        for map_id in [x for x in self.get_keys() if x not in [merge_name, ConfigName.comment]]:
            config = self.get(map_id, None)
            assert type(config) == dict, f"Must be dictionary {map_id}"
            assert len(config) > 0, f"Dictionary must be non empty {map_id}"
            result[map_id] = dict(merge_dict, **config)
        return result


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
        irig_notes = {"60": 80, "62": 90, "64": 100, "65": 110, "12": 40, "13": 50}
        MainLoader.__dl.add_if_missing(ConfigName.mapped_notes, irig_notes)
        kbd_notes = {'1': 60, '2': 62, '3': 64, '4': 65, 'q': 12, 'w': 13}
        MainLoader.__dl.add_if_missing(ConfigName.kbd_notes, kbd_notes)


if __name__ == "__main__":
    pass
