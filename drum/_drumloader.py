import logging
import os
from pathlib import Path
from typing import List, Any, Dict, Union, Tuple

import numpy as np
import soundfile as sf

from utils import JsonDictLoader, make_zero_buffer, record_sound_buff, MainLoader, SD_TYPE
from utils import MAX_SD, always_true, ConfigName


def extend_list(some_list: Union[List, str], new_len: int) -> List:
    """replicate or shrink list or string to a new length"""
    k = -(-new_len // len(some_list))
    return (some_list * k)[:new_len]


class DrumLoader:
    """Load drums"""

    swing: float = MainLoader.get(ConfigName.drum_swing, 0.75)
    volume: float = MainLoader.get(ConfigName.drum_volume, 1)
    patterns: List[np.ndarray] = []
    fills: List[np.ndarray] = []
    ends: List[np.ndarray] = []
    max_volume: float = 0
    length: int = 0
    __sounds: Dict[str, Tuple[np.ndarray, float]] = dict()
    __patterns: List[Dict[str, Any]] = []
    __fills: List[Dict[str, Any]] = []
    __ends: List[Dict[str, Any]] = []

    @classmethod
    def load(cls, dir_name: Path) -> None:
        assert always_true(f"Loading drum {dir_name}")
        if len(cls.__sounds) == 0:
            cls.__load_sounds(dir_name)
        cls.__load_all_patterns(dir_name, "drum_patterns", cls.__patterns)
        cls.__load_all_patterns(dir_name, "drum_fills", cls.__fills)
        cls.__load_all_patterns(dir_name, "drum_ends", cls.__ends)

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
            cls.max_volume = max(cls.max_volume, sound_vol)
            assert sound_vol < MAX_SD
            #  assert always_true(f"Loaded sound {file_name}")
            cls.__sounds[name] = (sound, volume)

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
            for sound_name in [x for x in cls.__sounds if x in pattern]:
                pattern[sound_name] = extend_list(pattern[sound_name], steps)
            storage.append(pattern)

    @classmethod
    def prepare_all(cls, length: int) -> None:
        cls.length = 0

        for j in [cls.fills, cls.patterns, cls.ends]:
            j.clear()

        for i in cls.__fills:
            cls.fills.append(cls.__prepare_one(i, length))

        for i in cls.__patterns:
            cls.patterns.append(cls.__prepare_one(i, length))

        for i in cls.__ends:
            cls.ends.append(cls.__prepare_one(i, length))

        cls.length = length

    @classmethod
    def __prepare_one(cls, pattern, length: int) -> np.ndarray:
        accents = pattern["accents"]
        ndarr = make_zero_buffer(length)
        drum_volume = MainLoader.get(ConfigName.drum_volume, 1)
        for sound_name in [x for x in DrumLoader.__sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                logging.error(f"sound {sound_name} notes {notes} must contain only '.' and '!'")

            step_len = length / steps
            sound, sound_volume = DrumLoader.__sounds[sound_name]
            sound = sound[:length]
            assert sound.ndim == 2 and sound.shape[1] == 2
            assert 0 < sound.shape[0] <= length, f"Must be: 0 < {sound.shape[0]} <= {length}"

            for step_number in range(steps):
                if notes[step_number] != '.':
                    step_accent = int(accents[step_number])
                    step_volume = sound_volume * step_accent * drum_volume / 9.0
                    pos = cls.__pos_with_swing(step_number, step_len)
                    tmp = (sound * step_volume).astype(SD_TYPE)
                    record_sound_buff(ndarr, tmp, pos)

        return ndarr

    @classmethod
    def __pos_with_swing(cls, step_number, step_len) -> int:
        """shift every even 16th note to make it swing like"""
        if step_number % 2 == 0:
            return round(step_number * step_len)
        else:
            swing_delta = step_len * (MainLoader.get(ConfigName.drum_swing, 0.625) - 0.5)
            return round(step_number * step_len + swing_delta)

    @classmethod
    def to_str(cls) -> str:
        return f"DrumLoader length: {cls.length}  patterns: {len(cls.patterns)} fills: {len(cls.fills)} " \
               f"ends: {len(cls.ends)} sounds: {len(cls.__sounds)} max_volume: {cls.max_volume}"


if __name__ == "__main__":
    pass
