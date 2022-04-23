from typing import List, Any

import numpy as np

from utils import record_sound_buff, play_sound_buff, SD_RATE, ScrColors, SD_MAX, val_str
from utils import sound_test, make_zero_buffer, MAX_LEN, always_true


class WrapBuffer:
    """buffer that can wrap over the end when get and set data. Can undo, redo"""

    def __init__(self, length: int = MAX_LEN):
        self.is_reverse: bool = False
        self.__is_empty = True
        self.__buff: np.ndarray = make_zero_buffer(length)
        self.__volume: float = -1
        self.__start: int = -1
        self.__undo: List[Any] = []
        self.__redo: List[Any] = []

    @property
    def length(self) -> int:
        return len(self.__buff)

    @property
    def is_empty(self) -> bool:
        return self.__is_empty

    def get_buff_copy(self) -> np.ndarray:
        return self.__buff.copy()

    def zero_buff(self) -> None:
        self.__buff[:] = 0

    def change_len(self, new_len: int) -> None:
        diff = new_len - self.length
        if diff > 0:
            self.__buff = np.concatenate((self.__buff[:], make_zero_buffer(diff)), axis=0)
        elif diff < 0:
            self.__buff = self.__buff[:new_len]

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

    def finalize(self, idx: int, trim_len: int = 0) -> None:
        """Trim is called once to fix buffer length. Buffer must be multiple of trim_len.
         If this length is negative use only idx value"""

        assert always_true(f"before trim: len {len(self.__buff)} trim_len {trim_len} start {self.__start} idx {idx}")

        assert self.__is_empty, f"buffer must be empty"
        assert self.__start >= 0, f"start must be non negative"

        if trim_len == len(self.__buff):
            self.__is_empty = False
            return

        if trim_len <= 0:
            assert self.__start == 0, f"start must be zero"
            assert idx < len(self.__buff), f"end of recording beyond buffer"
            self.__buff = self.__buff[:idx]
            self.__is_empty = False
            return

        idx = round(idx / trim_len) * trim_len
        self.__start %= trim_len
        if idx <= self.__start:
            idx += trim_len
        idx += self.__start

        assert idx < len(self.__buff), f"end of recording beyond buffer"
        self.__buff = self.__buff[self.__start:idx]

        assert always_true(f"after trim: len {len(self.__buff)} trim_len {trim_len} start {self.__start} idx {idx}")

        assert self.length % trim_len == 0 and self.length > 0, "incorrect buffer trim"
        self.__is_empty = False

    def redo(self) -> None:
        if len(self.__redo) > 0:
            self.__undo.append(self.__buff)
            self.__buff = self.__redo.pop()
            self.__volume = -1

    def get_undo_len(self) -> int:
        return len(self.__undo)

    def undo(self) -> None:
        if len(self.__undo) > 0:
            self.__redo.append(self.__buff)
            self.__buff = self.__undo.pop()
            self.__volume = -1

    def save_undo(self) -> None:
        if not self.is_empty:
            self.__redo.clear()
            self.__undo.append(self.__buff.copy())

    def info_str(self, cols: int) -> str:
        """Colored string to show volume and length"""
        if self.__is_empty:
            return val_str(0, 0, 1, cols)

        if self.__volume < 0:
            self.__volume = np.max(self.__buff) / SD_MAX

        tmp = val_str(self.__volume, 0, 1, cols)
        len_pos = round(self.length / MAX_LEN * cols)
        return ScrColors['reverse'] + tmp[:len_pos] + ScrColors['end'] + tmp[len_pos:]

    def __str__(self):
        return f"{self.__class__.__name__} sec={self.length / SD_RATE:.2f} " \
               f"vol={self.__volume:.2f} undo={len(self.__undo)} redo={len(self.__redo)}"


if __name__ == "__main__":
    pass
