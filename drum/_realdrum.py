import random
from enum import IntEnum
from threading import Timer

import numpy as np

from drum._drumloader import DrumLoader
from utils import MAX_32_INT, ConfigName, MainLoader, FileFinder, MAX_SD
from utils import SD_RATE, play_sound_buff


class Intensity(IntEnum):
    SILENT = 0
    FILL = 1
    PTRN = 2
    END = 4


def get_ending_intensity(i: int) -> int:
    """Intensity for drum ending"""
    return i * 2


def get_next_intensity(i: Intensity) -> int:
    """Cycle over intensities 1,2,3 only"""
    i = (i + 1) % Intensity.END
    return max(i, 1)


class RealDrum:
    """Drums generated from patterns with random changes"""

    change_after_bars: int = 3  # change pattern and fill after this many bars

    def __init__(self):
        self.__change_after_samples: int = MAX_32_INT
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
        tmp = self.__file_finder.get_path_now()
        DrumLoader.load(tmp)
        MainLoader.set(ConfigName.drum_type, self.__file_finder.get_item_now())
        MainLoader.save()

        if not self.is_empty:
            self.prepare_drum(self.length)

    def prepare_drum(self, length: int) -> None:
        """ Non blocking drum init in another thread, length is one bar long and holds drum pattern """
        Timer(0.2, DrumLoader.prepare_all, [length]).start()
        self.__change_after_samples = RealDrum.change_after_bars * length
        self.__intensity = Intensity.PTRN

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.__intensity == Intensity.SILENT or self.is_empty:
            return

        self.__sample_counter += len(out_data)
        if self.__sample_counter > self.__change_after_samples:
            self.__sample_counter = 0
            self.__pattern = random.randrange(len(DrumLoader.patterns))
            self.__fill = random.randrange(len(DrumLoader.fills))
            self.__end = random.randrange(len(DrumLoader.ends))

        if self.__intensity & Intensity.FILL == Intensity.FILL:
            play_sound_buff(DrumLoader.fills[self.__fill], out_data, idx)
        if self.__intensity & Intensity.PTRN == Intensity.PTRN:
            play_sound_buff(DrumLoader.patterns[self.__pattern], out_data, idx)
        if self.__intensity & Intensity.END == Intensity.END:
            play_sound_buff(DrumLoader.ends[self.__end], out_data, idx)

    def play_ending_later(self, part_len: int, idx: int) -> None:
        bars = 0.5 if random.random() < 0.5 else 1
        samples = self.length * bars
        idx %= part_len
        start_at = (part_len - idx) - samples
        if start_at > 0:
            Timer(start_at / SD_RATE, self.play_ending_now, (bars,)).start()

    def __set_intensity(self, i: Intensity) -> None:
        self.__intensity = i

    def play_ending_now(self, bars: float = 0) -> None:
        saved, elevated = self.__intensity, get_ending_intensity(self.__intensity)
        self.__sample_counter = 0
        self.__intensity = elevated
        if bars <= 0:
            bars = 0.5 if random.random() < 0.5 else 1
        samples = self.length * bars
        Timer(samples / SD_RATE, self.__set_intensity, (saved,)).start()

    def set_next_intensity(self) -> None:
        self.__intensity = get_next_intensity(self.__intensity)

    @staticmethod
    def change_drum_volume(change_by) -> None:
        factor = 1.41 if change_by >= 0 else 1 / 1.41
        DrumLoader.volume *= factor
        MainLoader.set(ConfigName.drum_volume, DrumLoader.volume)
        MainLoader.save()
        DrumLoader.prepare_all(DrumLoader.length)

    @staticmethod
    def change_swing(change_by) -> None:
        DrumLoader.swing = MainLoader.get(ConfigName.drum_swing, 0.625)
        delta = 0.25 / 4 if change_by >= 0 else -0.25 / 4
        DrumLoader.swing += delta
        DrumLoader.swing = max(min(DrumLoader.swing, 0.75), 0.5)
        if DrumLoader.swing != MainLoader.get(ConfigName.drum_swing, 0.625):
            MainLoader.set(ConfigName.drum_swing, DrumLoader.swing)
            MainLoader.save()
            DrumLoader.prepare_all(DrumLoader.length)

    def __str__(self):
        return f"RealDrum length: {self.length} empty: {self.is_empty} intensity: {self.__intensity}"
