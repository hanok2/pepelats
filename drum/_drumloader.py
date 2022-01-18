import os
from pathlib import Path
from typing import List, Any, Dict, Union, Tuple

import numpy as np
import soundfile as sf

from utils import JsonDictLoader
from utils import MAX_SD, always_true, ConfigName


def extend_list(some_list: Union[List, str], new_len: int) -> List:
    """replicate or shrink list or string to a new length"""
    k = -(-new_len // len(some_list))
    return (some_list * k)[:new_len]


class DrumLoader:
    """Load drums"""

    __max_volume: float = 0
    sounds: Dict[str, Tuple[np.ndarray, float]] = dict()
    patterns: List[Dict[str, Any]] = []
    fills: List[Dict[str, Any]] = []
    ends: List[Dict[str, Any]] = []

    @classmethod
    def get_max_volume(cls) -> float:
        return cls.__max_volume

    @classmethod
    def load(cls, dir_name: Path) -> None:
        assert always_true(f"Loading drum {dir_name}")
        if len(cls.sounds) == 0:
            cls.__load_sounds(dir_name)
        cls.__load_all_patterns(dir_name, "drum_patterns", cls.patterns)
        cls.__load_all_patterns(dir_name, "drum_fills", cls.fills)
        cls.__load_all_patterns(dir_name, "drum_ends", cls.ends)

    @classmethod
    def __load_sounds(cls, dir_name: Path) -> None:
        """Loads WAV sounds"""
        path = os.path.join(dir_name.parent, "drum_sounds.json")
        loader = JsonDictLoader(path)
        for name in loader.get_keys():
            drum_sound = loader.get(name, dict())
            assert len(drum_sound) > 0
            assert type(drum_sound) == dict
            file_name = drum_sound["file_name"]
            file_name = Path(loader.get_filename().parent, file_name)
            volume: float = drum_sound.get("volume", 1.0)

            (sound, _) = sf.read(str(file_name), dtype="int16", always_2d=True)
            assert sound.ndim == 2
            assert sound.shape[1] == 2
            sound_vol: float = np.max(sound) * volume
            cls.__max_volume = max(cls.__max_volume, sound_vol)
            assert sound_vol < MAX_SD
            #  assert always_true(f"Loaded sound {file_name}")
            cls.sounds[name] = (sound, volume)

    @classmethod
    def __load_all_patterns(cls, dir_name: Path, file_name: str, storage: List[Dict]) -> None:
        storage.clear()
        path = os.path.join(dir_name, file_name + ".json")
        loader = JsonDictLoader(path)
        default = loader.get(ConfigName.default_pattern, dict())
        excl_lst = [ConfigName.comment, ConfigName.default_pattern]
        for x, pattern in [(x, loader.get(x, None)) for x in loader.get_keys() if x not in excl_lst]:
            pattern = dict(default, **pattern)
            pattern["name"] = x
            pattern["___"] = ""
            steps: int = pattern["steps"]
            accents: str = pattern["accents"]
            pattern["accents"] = extend_list(accents, steps)
            for sound_name in [x for x in cls.sounds if x in pattern]:
                pattern[sound_name] = extend_list(pattern[sound_name], steps)
            storage.append(pattern)


if __name__ == "__main__":
    pass
