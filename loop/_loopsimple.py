from threading import Timer

import numpy as np

from loop._oneloopctrl import OneLoopCtrl
from loop._player import Player
from loop._wrapbuffer import WrapBuffer
from utils import MAX_LEN, STATE_COLS, ScrColors, always_true


class LoopSimple(WrapBuffer, Player):
    """Loop that may play and record itself. Has Control object to stop and keep loop index"""

    def __init__(self, ctrl: OneLoopCtrl, length: int = MAX_LEN):
        WrapBuffer.__init__(self, length)
        Player.__init__(self, ctrl)
        self.is_silent: bool = False

    def trim_buffer(self, idx: int) -> None:
        """trim buffer to the length at stop event = idx. Overridden by child class"""
        assert always_true(f"trim_buffer {self.__class__.__name__} idx {idx}")
        self.finalize(idx, 0)

    # noinspection PyUnusedLocal
    def state_str(self, is_now: bool, is_next: bool, is_rec: bool) -> str:
        """colored string to show state of loops"""
        if self.is_silent:
            full_str = '='
        elif self.is_reverse:
            full_str = '#'
        else:
            full_str = '*'

        count = min(STATE_COLS, self.get_undo_len() + 1)
        full_str = (full_str * count).rjust(STATE_COLS, '░')

        if is_now:
            tmp = (ScrColors['r'] if is_rec else ScrColors['g']) + full_str
        else:
            tmp = ScrColors['w'] + full_str

        return tmp + ScrColors['end']

    def __str__(self):
        return f"{WrapBuffer.__str__(self)} silent={self.is_silent} {self._ctrl}"


class LoopWithDrum(LoopSimple):
    """Loop truncate itself to be multiple of drum if drum is ready.
    Or init drum of correct length if drum is empty"""

    def __init__(self, ctrl: OneLoopCtrl, length: int = MAX_LEN):
        super().__init__(ctrl, length)

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self._ctrl.drum.play_samples(out_data, idx)
        if not self.is_silent:
            super().play_samples(out_data, idx)

    def trim_buffer(self, idx: int) -> None:
        """create drums of correct length if drum is empty,
        otherwise trims self.length to multiple of drum length"""
        assert always_true(f"trim_buffer {self.__class__.__name__} idx {idx}")
        if self._ctrl.drum.is_empty:
            self._ctrl.drum.prepare_drum(idx)
            self.finalize(idx, 0)
        else:
            self.finalize(idx, self._ctrl.drum.length)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle some fields
        del state["_ctrl"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Add _ctrl missing in the pickle
        self._ctrl = None


if __name__ == "__main__":
    def test1():
        c1 = OneLoopCtrl()
        c1._is_rec = True
        Timer(2, c1.stop_now).start()
        l1 = LoopSimple(c1)
        l1.play_buffer()
        c1.get_stop_event().clear()
        Timer(3, c1.stop_now).start()
        l1.play_buffer()


    def test2():
        c1 = OneLoopCtrl()
        c1._is_rec = True
        Timer(3.9, c1.stop_now).start()
        l1 = LoopWithDrum(c1)
        l1.play_buffer()
        c1.get_stop_event().clear()
        Timer(5, c1.stop_now).start()
        l1.play_buffer()


    test2()
