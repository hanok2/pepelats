import logging
import random
from enum import Enum
from threading import Timer
from typing import List, Any, Tuple

import numpy as np

from drum._drumloader import DrumLoader
from utils import MAX_LEN, MAX_32_INT, ConfigName, MainLoader, make_zero_buffer, record_sound_buff, \
    sound_test, FileFinder, MAX_SD
from utils import SD_TYPE, SD_RATE, play_sound_buff

EMPTY_ARR = np.ndarray([])


class Intensity(Enum):
    SILENT = 0
    FILL = 1
    PTRN = 2
    PTRN_FILL = 3
    ENDING = 4


def get_ending_intensities(i: Intensity) -> Tuple[Intensity, Intensity]:
    """Two new intensities - normal and elevated"""
    if i == Intensity.SILENT:
        return Intensity.FILL, Intensity.PTRN
    elif i == Intensity.FILL:
        return Intensity.FILL, Intensity.PTRN_FILL
    elif i == Intensity.PTRN:
        return Intensity.PTRN, Intensity.ENDING
    elif i == Intensity.PTRN_FILL:
        return Intensity.PTRN_FILL, Intensity.ENDING
    else:
        return Intensity.PTRN_FILL, Intensity.ENDING


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


DrumTupleType = Tuple[np.ndarray, np.ndarray, np.ndarray, Intensity]
EMPTY_DRUM: DrumTupleType = (EMPTY_ARR, EMPTY_ARR, EMPTY_ARR, Intensity.SILENT)


class RealDrum:
    """Drums generated from patterns with random changes"""

    change_after_bars: int = 3  # change pattern and fill after this many bars

    def __init__(self):
        self.__change_after_samples: int = MAX_32_INT
        self.__buff_len: int = MAX_LEN
        self.__sample_counter: int = 0
        self.__tuple: DrumTupleType = EMPTY_DRUM
        self.__patterns: List[np.ndarray] = []
        self.__fills: List[np.ndarray] = []
        self.__ends: List[np.ndarray] = []
        self.__drum_volume: float = MainLoader.get(ConfigName.drum_volume, 3.0)
        self.__swing: float = MainLoader.get(ConfigName.drum_swing, 0.625)
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
        p, f, e, i = self.__tuple
        self.__tuple = p, f, e, Intensity.SILENT

    def load_drum_type(self) -> None:
        if self.__file_finder.now == self.__file_finder.next:
            return
        self.__file_finder.now = self.__file_finder.next
        self.load()

        if not self.is_empty:
            self.prepare_drum(self.length)

    def prepare_drum(self, buff_len: int) -> None:
        """ Non blocking drum init in another thread, buff_len is one bar long and holds drum pattern """
        Timer(0.2, self.prepare_drum_blocking, [buff_len]).start()

    def prepare_drum_blocking(self, buff_len: int) -> None:
        self.__buff_len = buff_len
        self.__change_after_samples = buff_len * RealDrum.change_after_bars

        self.__tuple = EMPTY_DRUM
        self.__prep_all_patterns(DrumLoader.patterns, self.__patterns)
        self.__prep_all_patterns(DrumLoader.fills, self.__fills)
        self.__prep_all_patterns(DrumLoader.ends, self.__ends)
        self.__tuple = self.__patterns[0], self.__fills[0], self.__ends[0], Intensity.PTRN_FILL

    def __random_drum(self) -> DrumTupleType:
        p = random.randrange(len(self.__patterns))
        f = random.randrange(len(self.__fills))
        e = random.randrange(len(self.__ends))
        i = self.__tuple[3]
        return self.__patterns[p], self.__fills[f], self.__ends[e], i

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.is_empty:
            return

        self.__sample_counter += len(out_data)
        if self.__sample_counter > self.__change_after_samples:
            self.__sample_counter = 0
            self.__tuple = self.__random_drum()

        if self.__tuple[3] == Intensity.FILL:
            play_sound_buff(self.__tuple[1], out_data, idx)
        if self.__tuple[3] == Intensity.PTRN:
            play_sound_buff(self.__tuple[0], out_data, idx)
        elif self.__tuple[3] == Intensity.PTRN_FILL:
            play_sound_buff(self.__tuple[0], out_data, idx)
            play_sound_buff(self.__tuple[1], out_data, idx)
        elif self.__tuple[3] == Intensity.ENDING:
            play_sound_buff(self.__tuple[0], out_data, idx)
            play_sound_buff(self.__tuple[2], out_data, idx)
        else:
            pass

    def change_drum_at_end(self, part_len: int, idx: int) -> None:
        idx %= part_len
        start_at = (part_len - idx) - self.length // 2
        if start_at > 0:
            Timer(start_at / SD_RATE, self.change_drum_now).start()

    def change_drum_now(self) -> None:

        def assign_tuple(t: Tuple):
            self.__tuple = t

        p, f, e, k = self.__tuple
        i, j = get_ending_intensities(k)
        self.__tuple = p, f, e, j
        delay_samples = self.length // 2
        self.__sample_counter = 0
        Timer(delay_samples / SD_RATE, assign_tuple, ((p, f, e, i),)).start()

    def set_next_intensity(self) -> None:
        p, f, e, k = self.__tuple
        i = get_next_intensity(k)
        self.__tuple = p, f, e, i

    def __prep_all_patterns(self, loader_list: List[Any], storage: List[np.ndarray]) -> None:
        storage.clear()
        for i in loader_list:
            #  assert always_true(f"Pattern: {i}")
            storage.append(self.__prep_one_pattern(i))

    def __prep_one_pattern(self, pattern) -> np.ndarray:
        accents = pattern["accents"]
        ndarr = make_zero_buffer(self.length)
        for sound_name in [x for x in DrumLoader.sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                logging.error(f"type {self.__file_finder.get_item_now()} "
                              f"sound {sound_name} notes {notes} must contain only '.' and '!'")

            step_len = self.length / steps
            sound, sound_volume = DrumLoader.sounds[sound_name]
            sound = sound[:self.length]
            assert sound.ndim == 2 and sound.shape[1] == 2
            assert 0 < sound.shape[0] <= self.length, f"Must be: 0 < {sound.shape[0]} <= {self.length}"

            for step_number in range(steps):
                if notes[step_number] != '.':
                    step_accent = int(accents[step_number])
                    step_volume = sound_volume * step_accent * self.__drum_volume / 9.0
                    pos = self.__pos_with_swing(step_number, step_len)
                    tmp = (sound * step_volume).astype(SD_TYPE)
                    record_sound_buff(ndarr, tmp, pos)

        return ndarr

    def __pos_with_swing(self, step_number, step_len) -> int:
        """shift every even 16th note to make it swing like"""
        if step_number % 2 == 0:
            return round(step_number * step_len)
        else:
            swing_delta = step_len * (self.__swing - 0.5)
            return round(step_number * step_len + swing_delta)

    def change_drum_volume(self, change_by) -> None:
        factor = 1.41 if change_by >= 0 else 1 / 1.41
        new_volume = self.volume * factor
        if new_volume < 0.001 or new_volume > 1:
            return
        self.__drum_volume *= factor
        MainLoader.set(ConfigName.drum_volume, self.__drum_volume)
        MainLoader.save()
        self.prepare_drum_blocking(self.length)

    def change_swing(self, change_by) -> None:
        save_swing = self.__swing
        delta = 0.25 / 4 if change_by >= 0 else -0.25 / 4
        self.__swing += delta
        self.__swing = max(min(self.__swing, 0.75), 0.5)
        if save_swing != self.__swing:
            MainLoader.set(ConfigName.drum_swing, self.__swing)
            MainLoader.save()
            self.prepare_drum_blocking(self.length)

    def sound_test(self, duration_sec: float, record: bool) -> None:
        sound_test(self.__tuple[0], duration_sec, record)

    def __str__(self):
        return f"RealDrum length {self.length} empty {self.is_empty} intensity {self.__tuple[3]}"
