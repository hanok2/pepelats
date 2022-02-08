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
    END = 4


class RealDrum:
    """Drums generated from patterns with random changes"""

    change_after_bars: int = 3  # change pattern and fill after this many bars

    def __init__(self):
        self.__change_after_samples: int = MAX_32_INT
        self.__sample_counter: int = 0
        self.__i: Intensity = Intensity.SILENT
        self.__level2: int = 0
        self.__level1: int = 0
        self.__end: int = 0

        self.__file_finder = FileFinder("etc/drums", False, "", MainLoader.get(ConfigName.drum_type, "pop"))
        tmp = self.__file_finder.get_path_now()
        DrumLoader.load(tmp)

    def elevated_intensity(self) -> None:
        """Intensity for drum break"""
        if self.__i == Intensity.SILENT:
            self.__i = Intensity.LVL1
        elif self.__i == Intensity.LVL1:
            self.__i = Intensity.LVL1 + Intensity.END
        elif self.__i == Intensity.LVL2:
            self.__i = Intensity.LVL2 + Intensity.END
        else:
            self.__i = Intensity.LVL2

    def normal_intensity(self) -> None:
        """Intensity for drum break"""
        if self.__i & Intensity.LVL1:
            self.__i = Intensity.LVL1
        elif self.__i & Intensity.LVL2:
            self.__i = Intensity.LVL2
        else:
            self.__i = Intensity.LVL1

    def next_intensity(self) -> None:
        """Cycle over intensities 1,2 only"""
        if self.__i >= Intensity.LVL2:
            self.__i = Intensity.LVL1
        else:
            self.__i = Intensity.LVL2

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
        return f"  now  {self.__file_finder.get_item_now()}\n  next {self.__file_finder.get_item_next()}"

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
            self.__sample_counter = 0
            self.__level2 = random.randrange(len(DrumLoader.level2))
            self.__level1 = random.randrange(len(DrumLoader.level1))
            self.__end = random.randrange(len(DrumLoader.ends))

        if self.__i & Intensity.LVL1:
            play_sound_buff(DrumLoader.level1[self.__level1], out_data, idx)
        if self.__i & Intensity.LVL2:
            play_sound_buff(DrumLoader.level2[self.__level2], out_data, idx)
        if self.__i & Intensity.END:
            play_sound_buff(DrumLoader.ends[self.__end], out_data, idx)

    def play_ending_later(self, part_len: int, idx: int) -> None:
        bars = 0.5
        samples = self.length * bars
        idx %= part_len
        start_at = (part_len - idx) - samples
        if start_at > 0:
            Timer(start_at / SD_RATE, self.play_ending_now, (bars,)).start()

    def play_ending_now(self, bars: float = 0) -> None:
        self.__sample_counter = 0
        self.elevated_intensity()
        if bars <= 0:
            bars = 0.5 if random.random() < 0.5 else 1
        samples = self.length * bars
        Timer(samples / SD_RATE, self.normal_intensity).start()

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
        v = max(min(v, 0.75), 0.5)
        if v != MainLoader.get(ConfigName.drum_swing, 0.625):
            MainLoader.set(ConfigName.drum_swing, v)
            MainLoader.save()
            DrumLoader.prepare_all(DrumLoader.length)

    def __str__(self):
        return f"RealDrum length: {self.length} empty: {self.is_empty} intensity: {self.__i}"
