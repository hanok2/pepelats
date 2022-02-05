import logging
from typing import Dict, Any, List, Union

from utils import ConfigName, FileFinder, always_true
from utils import JsonDictLoader


class MidiConfigLoader:
    """Load MIDI notes mapping dict. from JSON files
    Dict[map_name, Dict[note, List[command, param1, ... ]]]
    To load this it parses etc/midi directory for JSON files"""

    ff: FileFinder = FileFinder("etc/midi", True, ".json", "")
    __map: Dict[str, Dict[str, List[Any]]] = dict()
    __map_name: str = ConfigName.playing_0

    for _ in range(ff.items_len):
        ff.iterate_dir(True)
        ff.now = ff.next
        file = ff.get_path_now()
        item = ff.get_item_now()
        assert always_true(f"Loading midi config {item} from {file}")
        loader = JsonDictLoader(file)
        default = loader.get(ConfigName.default_config, dict())
        result = dict()

        for key in [x for x in loader.get_keys() if x not in [ConfigName.default_config, ConfigName.comment]]:
            value = loader.get(key, None)
            assert type(value) == dict, f"Must be dictionary {key}"
            assert len(value) > 0, f"Dictionary must be non empty {key}"
            result[key] = dict(default, **value)

        __map.update(result)

    @classmethod
    def get(cls, key: str) -> Union[list[str, float], str]:
        return cls.__map[cls.__map_name].get(key, None)

    @classmethod
    def change_map(cls, new_name) -> None:
        if new_name in cls.__map:
            cls.__map_name = new_name
        elif new_name in ["prev", "next"]:
            prefix = cls.__map_name.split('_')[0]
            lst = [x for x in cls.__map if x.startswith(prefix)]
            k = lst.index(cls.__map_name) + (1 if new_name == "next" else -1)
            k %= len(lst)
            cls.__map_name = lst[k]
        else:
            logging.error(f"Incorrect MIDI map name: {new_name}")


if __name__ == "__main__":
    pass
