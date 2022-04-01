import random
from enum import IntEnum
from threading import Timer

import numpy as np

from drum._drumloader import DrumLoader
from utils import MAX_32_INT, ConfigName, MainLoader, FileFinder, SD_MAX
from utils import SD_RATE, play_sound_buff


class Intensity(IntEnum):
    SILENT = 0
    LVL1 = 1
    LVL2 = 2
    BREAK = 4

    @staticmethod
    def next(i: int) -> int:
        return 2 if i == 1 else 1


class RealDrum:
    """Drums generated from patterns with random changes"""

    change_after_bars: int = 3  # change pattern and fill after this many bars

    def __init__(self):
        self.__change_after_samples: int = MAX_32_INT
        self.__sample_counter: int = 0
        self.__i: Intensity = Intensity.SILENT

        self.__file_finder = FileFinder("etc/drums", False, "", MainLoader.get(ConfigName.drum_type, "pop"))
        tmp = self.__file_finder.get_path_now()
        DrumLoader.load(tmp)

    @staticmethod
    def clear() -> None:
        DrumLoader.length = 0

    @property
    def is_empty(self) -> bool:
        return DrumLoader.length == 0

    @property
    def length(self) -> int:
        return DrumLoader.length

    @property
    def volume(self) -> float:
        return MainLoader.get(ConfigName.drum_volume, 1) * DrumLoader.max_volume / SD_MAX

    @property
    def swing(self) -> float:
        return MainLoader.get(ConfigName.drum_swing, 0.75)

    def show_drum_type(self) -> str:
        return f"Now: {self.__file_finder.get_item_now()}   Next: {self.__file_finder.get_item_next()}"

    def change_drum_type(self, go_fwd: bool) -> None:
        self.__file_finder.iterate_dir(go_fwd)

    def silence_drum(self) -> None:
        self.__i = Intensity.SILENT

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
        self.__i = Intensity.LVL2

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.__i == Intensity.SILENT or self.is_empty:
            return

        self.__sample_counter += len(out_data)
        if self.__sample_counter > self.__change_after_samples:
            self.__random_samples()

        if self.__i & Intensity.LVL1:
            play_sound_buff(DrumLoader.get_l1(), out_data, idx)
        if self.__i & Intensity.LVL2:
            play_sound_buff(DrumLoader.get_l2(), out_data, idx)
        if self.__i & Intensity.BREAK:
            play_sound_buff(DrumLoader.get_bk(), out_data, idx)

    def play_ending_later(self, part_len: int, idx: int) -> None:
        bars = 0.5
        samples = self.length * bars
        idx %= part_len
        start_at = (part_len - idx) - samples
        if start_at > 0:
            Timer(start_at / SD_RATE, self.play_ending_now, (bars,)).start()

    def __random_samples(self):
        self.__sample_counter = 0
        DrumLoader.random_samples()

    def play_ending_now(self, bars: float = 0) -> None:
        if self.__i == Intensity.SILENT:
            self.__i = Intensity.LVL1

        def revert():
            self.__i &= ~Intensity.BREAK

        self.__random_samples()
        self.__i |= Intensity.BREAK
        if bars <= 0:
            bars = 0.5 if random.random() < 0.5 else 1
        samples = self.length * bars
        Timer(samples / SD_RATE, revert).start()

    @staticmethod
    def change_drum_volume(change_by) -> None:
        factor = 1.41 if change_by >= 0 else (1 / 1.41)
        v = MainLoader.get(ConfigName.drum_volume, 1) * factor
        if v * DrumLoader.max_volume >= SD_MAX:
            return
        if v * DrumLoader.max_volume < 0.01 * SD_MAX:
            return
        MainLoader.set(ConfigName.drum_volume, v)
        MainLoader.save()
        DrumLoader.prepare_all(DrumLoader.length)

    @staticmethod
    def change_swing(change_by) -> None:
        v = MainLoader.get(ConfigName.drum_swing, 0.625)
        v += (0.25 / 4) if change_by >= 0 else (-0.25 / 4)
        if v > 0.80:
            v = 0.50
        elif v < 0.45:
            v = 0.75

        MainLoader.set(ConfigName.drum_swing, v)
        MainLoader.save()
        DrumLoader.prepare_all(DrumLoader.length)

    def next_intensity(self) -> None:
        """Cycle over intensities 1,2 only"""
        self.__i = 1 if self.__i == 2 else 2

    def __str__(self):
        return f"RealDrum length: {self.length} empty: {self.is_empty} intensity: {self.__i}"
