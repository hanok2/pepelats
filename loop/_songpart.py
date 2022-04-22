import numpy as np

from loop._loopsimple import LoopWithDrum
from loop._oneloopctrl import OneLoopCtrl
from loop._player import Player
from loop._wrapbuffer import WrapBuffer
from utils import CollectionOwner, ScrColors
from utils import STATE_COLS


class SongPart(CollectionOwner[LoopWithDrum], Player):
    """Loop that includes many more simple loops to play together"""

    def __init__(self, ctrl: OneLoopCtrl):
        Player.__init__(self, ctrl)
        CollectionOwner.__init__(self)
        self.items.append(LoopWithDrum(ctrl))

    def trim_buffer(self, idx: int) -> None:
        loop = self.get_item_now()
        if self.now == 0:
            loop.trim_buffer(idx)
            return

        recorded_len = loop.get_recorded_len(idx)
        drum_len = self._ctrl.drum.length
        if recorded_len < drum_len // 2:
            loop.finalize(idx, drum_len)
        else:
            init_len = self.items[0].length
            loop.finalize(idx, init_len)

    @property
    def is_empty(self) -> bool:
        return self.get_item_now().is_empty

    @property
    def length(self) -> int:
        return self.items[0].length

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self._ctrl.drum.play_samples(out_data, idx)
        for loop in self.items:
            if not loop.is_silent:
                WrapBuffer.play_samples(loop, out_data, idx)

    def record_samples(self, in_data: np.ndarray, idx: int) -> None:
        loop = self.get_item_now()
        WrapBuffer.record_samples(loop, in_data, idx)

    def state_str(self, is_now: bool, is_next: bool) -> str:
        """colored string to show state of loops"""
        count = min(self.items_len, STATE_COLS)
        full_str = '■' * count
        full_str = full_str.rjust(STATE_COLS, '░')

        if is_now:
            tmp = (ScrColors['r'] if self._ctrl.is_rec else ScrColors['g']) + full_str
        elif is_next:
            tmp = (ScrColors['y'] if self._ctrl.is_stop_len_set() else ScrColors['v']) + full_str
        else:
            tmp = ScrColors['w'] + full_str

        return tmp + ScrColors['end']

    def __str__(self):
        return f"{self.__class__.__name__} items={self.items_len} redo={len(self.backup)}"


if __name__ == "__main__":
    pass
