from abc import abstractmethod

import numpy as np
import sounddevice as sd

from loop._oneloopctrl import OneLoopCtrl
from utils import always_true


class Player:
    """Abstract class that can play record using sounddevice"""

    def __init__(self, ctrl: OneLoopCtrl):
        self._ctrl: OneLoopCtrl = ctrl

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
            self.trim_buffer(self._ctrl.idx)

        assert always_true(f"======Stop {self}")

    @abstractmethod
    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        pass

    @abstractmethod
    def record_samples(self, in_data: np.ndarray, idx: int) -> None:
        pass

    @abstractmethod
    def trim_buffer(self, idx: int) -> None:
        pass

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def state_str(self, is_now: bool, is_next: bool) -> str:
        pass

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle some fields
        del state["_ctrl"]
        return state
