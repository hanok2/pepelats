import random
from enum import Enum
from threading import Timer
from typing import List, Tuple

import numpy as np

from drum._drumloader import DrumLoader
from utils import MAX_LEN, MAX_32_INT, ConfigName, MainLoader, make_zero_buffer, FileFinder, MAX_SD, sound_test
from utils import SD_RATE, play_sound_buff

EMPTY_ARR = np.ndarray([])


class Intensity(Enum):
    SILENT = 0
    FILL = 1
    PTRN = 2
    PTRN_FILL = 3
    ENDING = 4


def get_ending(i: Intensity) -> Tuple[Intensity, Intensity, bool]:
    """Two new intensities - normal and elevated, and bool to play elevated longer"""
    longer: bool = random.random() < 0.5
    if i == Intensity.SILENT:
        return Intensity.FILL, Intensity.PTRN, longer
    elif i == Intensity.FILL:
        return Intensity.FILL, Intensity.PTRN_FILL, longer
    elif i == Intensity.PTRN:
        return Intensity.PTRN, Intensity.ENDING, longer
    elif i == Intensity.PTRN_FILL:
        return Intensity.PTRN_FILL, Intensity.ENDING, longer
    else:
        return Intensity.PTRN_FILL, Intensity.ENDING, longer


def get_next_intensity(i: Intensity) -> Intensity:
    """Cycle intensities except SILEND and ENDING"""
    if i == Intensity.SILENT:
        return Intensity.FILL
    elif i == Intensity.FILL:
        return Intensity.PTRN
    elif i == Intensity.PTRN:
        return Intensity.PTRN_FILL
    elif i == Intensity.PTRN_FILL:
        return Intensity.FILL
    else:
        return Intensity.PTRN_FILL


class RealDrum:
    """Drums generated from patterns with random changes"""

    change_after_bars: int = 3  # change pattern and fill after this many bars

    def __init__(self):
        self.__change_after_samples: int = MAX_32_INT
        self.__buff_len: int = MAX_LEN
        self.__buffer: np.ndarray = EMPTY_ARR
        self.__sample_counter: int = 0
        self.__intensity: Intensity = Intensity.SILENT
        self.__patterns: List[np.ndarray] = []
        self.__fills: List[np.ndarray] = []
        self.__ends: List[np.ndarray] = []

        self.__file_finder = FileFinder("etc/drums", False, "", MainLoader.get(ConfigName.drum_type, "pop"))
        tmp = self.__file_finder.get_path_now()
        DrumLoader.load(tmp)

    def clear(self):
        self.__buff_len = MAX_LEN

    def load(self):
        tmp = self.__file_finder.get_path_now()
        DrumLoader.load(tmp)
        MainLoader.set(ConfigName.drum_type, self.__file_finder.get_item_now())
        MainLoader.save()

    @property
    def is_empty(self) -> bool:
        return self.__buff_len >= MAX_LEN

    @property
    def length(self) -> int:
        return self.__buff_len

    @property
    def volume(self) -> float:
        return DrumLoader.get_max_volume() * self.__drum_volume / MAX_SD

    @property
    def swing(self) -> float:
        return self.__swing

    def show_drum_type(self) -> str:
        return f"  now  {self.__file_finder.get_item_now()}\n  next {self.__file_finder.get_item_next()}"

    def change_drum_type(self, go_fwd: bool) -> None:
        self.__file_finder.iterate_dir(go_fwd)

    def silence_drum(self) -> None:
        self.__intensity = Intensity.SILENT

    def load_drum_type(self) -> None:
        if self.__file_finder.now == self.__file_finder.next:
            return
        self.__file_finder.now = self.__file_finder.next
        self.load()

        if not self.is_empty:
            self.prepare_drum(self.length)

    def prepare_drum(self, buff_len: int) -> None:
        """ Non blocking drum init in another thread, buff_len is one bar long and holds drum pattern """
        Timer(0.2, DrumLoader.prepare_drum_blocking, [buff_len]).start()

    def prepare_drum_blocking(self, buff_len: int) -> None:
        self.__buffer = make_zero_buffer(buff_len)
        self.__buff_len = buff_len
        self.__change_after_samples = buff_len * RealDrum.change_after_bars
        self.__prep_all_patterns(DrumLoader.patterns, self.__patterns)
        self.__prep_all_patterns(DrumLoader.fills, self.__fills)
        self.__prep_all_patterns(DrumLoader.ends, self.__ends)
        self.__random_drum()

    def __random_drum(self) -> None:
        p = random.randrange(len(self.__patterns))
        f = random.randrange(len(self.__fills))
        e = random.randrange(len(self.__ends))

        if self.__intensity == Intensity.FILL:
            self.__buffer = f
        elif self.__intensity == Intensity.PTRN:
            self.__buffer = p
        elif self.__intensity == Intensity.PTRN_FILL:
            self.__buffer = p + f
        elif self.__intensity == Intensity.ENDING:
            self.__buffer = p + e
        else:
            pass

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.__intensity == Intensity.SILENT or self.is_empty:
            return

        self.__sample_counter += len(out_data)
        if self.__sample_counter > self.__change_after_samples:
            self.__sample_counter = 0
            self.__random_drum()

        play_sound_buff(self.__buffer, out_data, idx)

    def change_drum_at_end(self, part_len: int, idx: int) -> None:
        idx %= part_len
        start_at = (part_len - idx) - self.length // 2
        if start_at > 0:
            Timer(start_at / SD_RATE, self.change_drum_now).start()

    def change_drum_now(self) -> None:

        def assign_tuple(t: Tuple):
            self.???????????? = t

        p, f, e, k = self.????????????
        i, j, longer = get_ending(k)
        self.???????????? = p, f, e, j
        delay_samples = self.length if longer else self.length // 2
        self.__sample_counter = 0
        Timer(delay_samples / SD_RATE, assign_tuple, ((p, f, e, i),)).start()

    def set_next_intensity(self) -> None:
        i = get_next_intensity(self.__intensity)
        self.???????????? = p, f, e, i







    def sound_test(self, duration_sec: float, record: bool) -> None:
        sound_test(self.__buffer, duration_sec, record)

    def __str__(self):
        return f"RealDrum length {self.length} empty {self.is_empty} intensity {self.__intensity}"
