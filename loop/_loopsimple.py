import numpy as np
import sounddevice as sd

from loop._oneloopctrl import OneLoopCtrl
from loop._wrapbuffer import WrapBuffer
from utils import MAX_LEN, CollectionOwner, always_true, STATE_COLS


class LoopSimple(WrapBuffer):
    """Loop that may play and record itself. Has Control object to stop and keep loop index"""

    def __init__(self, ctrl: OneLoopCtrl, length: int = MAX_LEN):
        super().__init__(length)
        self.is_silent: bool = False
        self._ctrl: OneLoopCtrl = ctrl

    def trim_buffer(self, idx, trim_len: int) -> None:
        """trim buffer to the length at stop event = idx. Overridden by child class"""
        WrapBuffer.trim_buffer(self, idx, -1)

    def play_buffer(self):
        assert always_true(f"======Start {self}")

        # noinspection PyUnusedLocal
        def callback(in_data, out_data, frame_count, time_info, status):

            out_data[:] = 0
            assert len(out_data) == len(in_data) == frame_count
            self.play_samples(out_data, self._ctrl.idx)

            if self._ctrl.is_rec:
                self.record_samples(in_data, self._ctrl.idx)

            self._ctrl.idx += frame_count
            if self._ctrl.idx >= self._ctrl.get_stop_len():
                self._ctrl.stop_now()

        with sd.Stream(callback=callback):
            self._ctrl.get_stop_event().wait()

        if self.is_empty:
            self.trim_buffer(self._ctrl.idx, -1)

        assert always_true(f"======Stop {self}")

    def state_str(self, owner: CollectionOwner) -> str:
        """colored string to show state of loops"""
        if self.is_silent:
            full_str = '='
        elif self.is_reverse:
            full_str = '#'
        else:
            full_str = '*'

        count = min(STATE_COLS, self.get_undo_len() + 1)
        full_str = (full_str * count).rjust(STATE_COLS, '░')
        part_id = owner.items.index(self)
        if part_id == owner.now:
            return ('r' if self._ctrl.is_rec else 'g') + full_str
        else:
            return 'w' + full_str

    def __str__(self):
        return f"{WrapBuffer.__str__(self)} silent={self.is_silent} {self._ctrl}"


class LoopWithDrum(LoopSimple):
    """Loop truncate itself to be multiple of drum if drum is ready.
    Or init drum of correct length if drum is empty"""

    def __init__(self, ctrl: OneLoopCtrl, length: int = MAX_LEN):
        super().__init__(ctrl, length)

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self._ctrl.drum.play_samples(out_data, idx)
        if not self.is_silent and not self.is_empty:
            super().play_samples(out_data, idx)

    def trim_buffer(self, idx, trim_len: int) -> None:
        """create drums of correct length if drum is empty,
        otherwise trims self.length to multiple of drum length"""
        if self._ctrl.drum.is_empty:
            self._ctrl.drum.prepare_drum(idx % MAX_LEN)
            WrapBuffer.trim_buffer(self, idx, -1)
        else:
            recorded_len = self.get_recorded_len(idx)
            if trim_len <= 0 or recorded_len < trim_len // 2:
                WrapBuffer.trim_buffer(self, idx, self._ctrl.drum.length)
            else:
                WrapBuffer.trim_buffer(self, idx, trim_len)

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
    pass
