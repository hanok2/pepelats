import random
from enum import Enum
from threading import Timer
from typing import Tuple

import numpy as np

from drum._drumloader import DrumLoader
from utils import MAX_32_INT, ConfigName, MainLoader, FileFinder, MAX_SD, make_zero_buffer
from utils import SD_RATE, play_sound_buff

EMPTY_ARR = make_zero_buffer(20)


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
        self.__buffer: np.ndarray = EMPTY_ARR
        self.__sample_counter: int = 0
        self.__intensity: Intensity = Intensity.SILENT
        self.__pattern: int = 0
        self.__fill: int = 0
        self.__end: int = 0

        self.__file_finder = FileFinder("etc/drums", False, "", MainLoader.get(ConfigName.drum_type, "pop"))
        tmp = self.__file_finder.get_path_now()
        DrumLoader.load(tmp)

    @staticmethod
    def clear():
        DrumLoader.length = 0

    def load(self):
        tmp = self.__file_finder.get_path_now()
        DrumLoader.load(tmp)
        MainLoader.set(ConfigName.drum_type, self.__file_finder.get_item_now())
        MainLoader.save()

    @property
    def is_empty(self) -> bool:
        return DrumLoader.length == 0

    @property
    def length(self) -> int:
        return DrumLoader.length

    @property
    def volume(self) -> float:
        return DrumLoader.volume * DrumLoader.max_volume / MAX_SD

    @property
    def swing(self) -> float:
        return DrumLoader.swing

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

    def prepare_drum(self, length: int) -> None:
        """ Non blocking drum init in another thread, length is one bar long and holds drum pattern """
        Timer(0.2, DrumLoader.prepare_all, [length]).start()
        self.__intensity = Intensity.PTRN_FILL

    def __random_drum(self) -> None:
        self.__pattern = random.randrange(len(DrumLoader.patterns))
        self.__fill = random.randrange(len(DrumLoader.fills))
        self.__end = random.randrange(len(DrumLoader.ends))

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.__intensity == Intensity.SILENT or self.is_empty:
            return

        self.__sample_counter += len(out_data)
        if self.__sample_counter > self.__change_after_samples:
            self.__sample_counter = 0
            self.__random_drum()

        if self.__intensity == Intensity.FILL:
            play_sound_buff(DrumLoader.fills[self.__fill], out_data, idx)
        elif self.__intensity == Intensity.PTRN:
            play_sound_buff(DrumLoader.patterns[self.__pattern], out_data, idx)
        elif self.__intensity == Intensity.PTRN_FILL:
            play_sound_buff(DrumLoader.fills[self.__fill], out_data, idx)
            play_sound_buff(DrumLoader.patterns[self.__pattern], out_data, idx)
        elif self.__intensity == Intensity.ENDING:
            play_sound_buff(DrumLoader.ends[self.__end], out_data, idx)
            play_sound_buff(DrumLoader.patterns[self.__pattern], out_data, idx)
        else:
            pass

    def play_ending_later(self, part_len: int, idx: int) -> None:
        idx %= part_len
        start_at = (part_len - idx) - self.length // 2
        if start_at > 0:
            Timer(start_at / SD_RATE, self.play_ending_now).start()

    def __set_intensity(self, i: Intensity) -> None:
        self.__intensity = i

    def play_ending_now(self) -> None:
        normal, elevated, longer = get_ending(self.__intensity)
        delay_samples = self.length if longer else self.length // 2
        self.__sample_counter = 0
        self.__intensity = elevated
        Timer(delay_samples / SD_RATE, self.__set_intensity, (normal,)).start()

    def set_next_intensity(self) -> None:
        self.__intensity = get_next_intensity(self.__intensity)

    def __str__(self):
        return f"RealDrum length: {self.length} empty: {self.is_empty} intensity: {self.__intensity}"
