from math import log
from typing import List, Any

import numpy as np

from utils import record_sound_buff, play_sound_buff, SD_RATE, ScrColors
from utils import sound_test, make_zero_buffer, MAX_LEN, MAX_SD


class WrapBuffer:
    """buffer that can wrap over the end when get and set data. Can undo, redo"""

    def __init__(self, length: int = MAX_LEN):
        self.is_reverse: bool = False
        self.__is_empty = length == MAX_LEN
        self.__buff: np.ndarray = make_zero_buffer(length)
        self.__volume: float = -1
        self.__length: int = length
        self.__start: int = -1
        self.__undo: List[Any] = []
        self.__redo: List[Any] = []

    @property
    def volume(self) -> float:
        if self.__is_empty:
            return 0
        if self.__volume < 0:
            tmp = np.max(self.__buff)
            self.__volume = round(float(tmp) / MAX_SD, 3)
        return self.__volume

    @property
    def length(self) -> int:
        return self.__length

    @property
    def is_empty(self) -> bool:
        return self.__is_empty

    def get_buff_copy(self) -> np.ndarray:
        return self.__buff.copy()

    def zero_buff(self) -> None:
        self.__buff[:] = 0

    def record_samples(self, in_data: np.ndarray, idx: int) -> None:
        """Record and fix start for empty, recalculate volume for non empty"""
        if self.__is_empty:
            if self.__start < 0:
                self.__start = idx
        elif self.__volume >= 0:
            self.__volume = -1

        record_sound_buff(self.__buff, in_data, idx)

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        tmp = self.__buff[::-1] if self.is_reverse else self.__buff
        play_sound_buff(tmp, out_data, idx)

    def sound_test(self, duration_sec: float, record: bool) -> None:
        sound_test(self.__buff, duration_sec, record)

    def get_recorded_len(self, idx: int) -> int:
        if self.__start < 0:
            return 0
        else:
            return idx - self.__start

    def trim_buffer(self, idx: int, trim_len: int) -> None:
        """Trim is called once to fix buffer length. Buffer must be multiple of trim_len.
         If this length is negative use only idx value"""
        assert self.__is_empty, "Trimmed buffer must be empty"
        assert idx > self.__start, "Trimmed buffer must have: idx {idx} > self.__start {self.__start}"
        assert self.__start >= 0, f"Trim without recording! self.__start {self.__start}"

        if trim_len > 0:
            idx = round(idx / trim_len) * trim_len
            self.__start = round(self.__start / trim_len) * trim_len
            if idx == self.__start:
                idx += trim_len
        else:
            assert self.__start == 0, f"self.__start {self.__start}"

        idx %= MAX_LEN
        self.__start %= MAX_LEN
        if idx > self.__start:
            self.__buff = self.__buff[self.__start:idx]
        else:
            self.__buff = np.concatenate((self.__buff[self.__start:], self.__buff[:idx]), axis=0)

        self.__length = len(self.__buff)
        assert trim_len <= 0 or self.__length % trim_len == 0, \
            f"self.__length {self.__length} trim_len {trim_len} self.__start {self.__start} idx {idx}"
        self.__is_empty = False
        self.__volume = -1

    def redo(self) -> None:
        if len(self.__redo) > 0:
            self.__undo.append(self.__buff)
            self.__buff = self.__redo.pop()
            self.__length = len(self.__buff)
            self.__volume = -1

    def get_undo_len(self) -> int:
        return len(self.__undo)

    def undo(self) -> None:
        if len(self.__undo) > 0:
            self.__redo.append(self.__buff)
            self.__buff = self.__undo.pop()
            self.__length = len(self.__buff)
            self.__volume = -1

    def save_undo(self) -> None:
        if not self.is_empty:
            self.__redo.clear()
            self.__undo.append(self.__buff.copy())

    def info_str(self, cols: int) -> str:
        """Colored string to show volume and length. Volume uses color inversion"""
        volume_db = 20 * log(max(self.volume, 0.001), 10)  # from -60 decibeb to 0 decibel
        volume_db += 60  # from 0 to +60
        assert 0 <= volume_db <= 60, "Must be: 0 <= volume_db <= 60"
        len_pos: int = 0 if self.is_empty else round(self.length / MAX_LEN * cols)
        vol_pos: int = round(volume_db / 60 * cols)
        tmp = '—' * vol_pos + '╬' + '-' * (cols - vol_pos - 1)
        if len_pos > 0:
            tmp = ScrColors['reverse'] + tmp[:len_pos] + ScrColors['end'] + tmp[len_pos:]
        return tmp

    def __str__(self):
        return f"{self.__class__.__name__} sec={self.length / SD_RATE:.2f} " \
               f"vol={self.volume:.2f} undo={len(self.__undo)} redo={len(self.__redo)}"


if __name__ == "__main__":
    pass
