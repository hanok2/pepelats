import logging
from json import load, dump
from pathlib import Path
from typing import Any, List, Dict, Union

from utils._utilsother import ROOT_DIR, ConfigName, FileFinder, always_true


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


def load_all_dics() -> Dict[str, Dict[str, Dict]]:
    dic = dict()
    ff: FileFinder = FileFinder("etc/midi", True, ".json", "")
    for _ in range(ff.items_len):
        ff.iterate_dir(True)
        ff.now = ff.next
        file = ff.get_path_now()
        item = ff.get_item_now()[:-len(ff.get_end_with())]
        assert always_true(f"Loading midi config from {file}")
        loader = JsonDictLoader(file)
        default_dic = loader.get(ConfigName.default_config, dict())
        dic1 = dict()

        for key in [x for x in loader.get_keys() if x not in [ConfigName.default_config, ConfigName.comment]]:
            value = loader.get(key, None)
            assert type(value) == dict, f"Must be dictionary key={key} in file {item}"
            assert len(value) > 0, f"Dictionary must be non empty key={key} in file {item}"
            dic1[key] = dict(default_dic, **value)

        dic[item] = dic1

    return dic


class MidiConfigLoader:
    """ class will only static methods to keep
    MIDI notes mapping dict. from JSON files
    It parses etc/midi directory for JSON files """

    __items: Dict[str, Dict] = load_all_dics()
    __map_name: str = ConfigName.playing
    __map_id: str = "0"

    @staticmethod
    def get(key: str) -> Union[List, None]:
        tmp1: Dict = MidiConfigLoader.__items[MidiConfigLoader.__map_name]
        tmp2: Dict = tmp1[MidiConfigLoader.__map_id]
        return tmp2.get(key, None)

    @staticmethod
    def change_map(new_id: str, new_name: str = "") -> None:
        if new_name:
            if new_name not in MidiConfigLoader.__items:
                logging.error(f"Incorrect MIDI map name: {new_name}")
                return
            else:
                MidiConfigLoader.__map_name = new_name

        tmp: Dict = MidiConfigLoader.__items[MidiConfigLoader.__map_name]
        if new_id in tmp:
            MidiConfigLoader.__map_id = new_id
        elif new_id in ["prev", "next"]:
            lst = list(tmp.values())
            k = lst.index(MidiConfigLoader.__map_id) + (1 if new_id == "next" else -1)
            k %= len(lst)
            MidiConfigLoader.__map_id = lst[k]
        else:
            logging.error(f"Incorrect MIDI map id: {new_id} for map {MidiConfigLoader.__map_name}")


if __name__ == "__main__":
    pass
