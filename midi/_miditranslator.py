import logging
from multiprocessing.connection import Connection
from typing import Dict, Union, List

from utils import ConfigName, always_true, FileFinder, JsonDictLoader


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
    def change_map(new_id: str, new_name: str) -> None:
        if new_name not in MidiConfigLoader.__items:
            logging.error(f"Incorrect MIDI map name: {new_name}")
            return
        else:
            MidiConfigLoader.__map_name = new_name

        tmp: Dict = MidiConfigLoader.__items[MidiConfigLoader.__map_name]
        if new_id in tmp:
            MidiConfigLoader.__map_id = new_id
        elif new_id in ["prev", "next"]:
            lst = list(tmp.keys())
            k = lst.index(MidiConfigLoader.__map_id) + (1 if new_id == "next" else -1)
            k %= len(lst)
            MidiConfigLoader.__map_id = lst[k]
        else:
            logging.error(f"Incorrect MIDI map id: {new_id} for map {MidiConfigLoader.__map_name}")


class MidiTranslator:
    """Translate note to command with parameters and sends to a connection"""

    def __init__(self, s_conn: Connection):
        self.__s_conn = s_conn

    def translate_and_send(self, note: str) -> None:
        msg = MidiConfigLoader.get(note)
        if msg is not None:
            method_name, *params = msg
            assert always_true(f"Sending message: {msg}")
            if method_name == ConfigName.change_map:
                MidiConfigLoader.change_map(params[0], params[1])
            else:
                self.__s_conn.send(msg)
            update_method = MidiConfigLoader.get(ConfigName.update_method)
            description = MidiConfigLoader.get(ConfigName.description)
            msg = [ConfigName.redraw, update_method, description]
            assert always_true(f"Sending message: {msg}")
            self.__s_conn.send(msg)
        else:
            pass
