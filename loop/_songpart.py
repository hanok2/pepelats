from typing import List

import numpy as np

from loop._loopsimple import LoopWithDrum
from loop._oneloopctrl import OneLoopCtrl
from loop._wrapbuffer import WrapBuffer
from utils import CollectionOwner, SCR_COLS, ScrColors
from utils import MAX_LEN
from utils import STATE_COLS


class SongPart(CollectionOwner[LoopWithDrum], LoopWithDrum):
    """Loop that includes many more simple loops to play together"""

    def __init__(self, ctrl: OneLoopCtrl, length: int = MAX_LEN):
        LoopWithDrum.__init__(self, ctrl, length)
        CollectionOwner.__init__(self)
        self.__redo: List[LoopWithDrum] = []
        self.items.append(self)

    def save_undo(self) -> None:
        if not self.is_empty:
            self.__redo.clear()
            self.items.append(LoopWithDrum(self._ctrl, self.length))
            self.now = self.next = self.items_len - 1

    def undo(self) -> None:
        if self.items_len > 1:
            self.now = self.next = 0
            self.__redo.append(self.items.pop())

    def redo(self) -> None:
        if len(self.__redo) > 0:
            self.items.append(self.__redo.pop())

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self._ctrl.drum.play_samples(out_data, idx)
        for loop in self.items:
            if not self.is_silent:
                WrapBuffer.play_samples(loop, out_data, idx)

    @property
    def is_empty(self) -> bool:
        loop = self.get_item_now()
        return super(LoopWithDrum, loop).is_empty

    def record_samples(self, in_data: np.ndarray, idx: int) -> None:
        loop = self.get_item_now()
        WrapBuffer.record_samples(loop, in_data, idx)

    def info_str(self, cols: int) -> str:
        """colored string to show volume and length"""
        tmp = ""
        for loop in self.items:
            assert self._ctrl.drum.is_empty or loop.is_empty or loop.length % self._ctrl.drum.length == 0, \
                f"loop: {loop.length} drum: {self._ctrl.drum.length}"
            state_str = LoopWithDrum.state_str(loop, self)
            tmp += state_str + LoopWithDrum.info_str(loop, SCR_COLS - STATE_COLS) + "\n"
        return tmp[:-1]

    def state_str(self, owner: CollectionOwner) -> str:
        """colored string to show state of loops"""
        count = min(self.items_len, STATE_COLS)
        full_str = '■' * count
        full_str = full_str.rjust(STATE_COLS, '░')
        part_id = owner.items.index(self)
        if part_id == owner.now:
            tmp = (ScrColors['r'] if self._ctrl.is_rec else ScrColors['g']) + full_str
        elif part_id == owner.next:
            tmp = (ScrColors['y'] if self._ctrl.is_stop_len_set() else ScrColors['v']) + full_str
        else:
            tmp = ScrColors['w'] + full_str

        return tmp + ScrColors['end']

    def __str__(self):
        return f"{LoopWithDrum.__str__(self)} items={self.items_len} redo={len(self.__redo)}"


if __name__ == "__main__":
    pass
