import time
import unittest
from threading import Timer
from typing import Tuple

# noinspection PyProtectedMember
from loop._loopsimple import LoopWithDrum
# noinspection PyProtectedMember
from loop._oneloopctrl import OneLoopCtrl
from utils import SD_RATE


def record_with_drum(samples: int, control: OneLoopCtrl) -> Tuple[int, int]:
    control.get_stop_event().clear()
    control._is_rec = True
    loop = LoopWithDrum(control)
    Timer(samples / SD_RATE, control.stop_now).start()
    loop.play_buffer()
    while control.drum.is_empty:
        time.sleep(0.1)
    return loop.length, control.idx


class TestLoopWithDrum(unittest.TestCase):
    """integration test of 2 classes"""

    def test_1(self):
        """Test control attributes"""
        control = OneLoopCtrl()
        self.assertFalse(control.is_rec)
        self.assertFalse(control.is_stop_len_set())
        self.assertFalse(control.get_stop_event().is_set())

    def test_2(self):
        """Test control drum and loop length"""
        # Test new recorded loop is multiple of drum if drum non empty
        control = OneLoopCtrl()
        control.drum.prepare_drum(100_000)
        while control.drum.is_empty:
            time.sleep(0.1)

        loop_len, idx = record_with_drum(240_000, control)
        self.assertTrue(loop_len % 100_000 == 0)

        # Test new recorded loop is equal to drum if drum was empty
        control.drum.clear()
        control.idx = 0
        loop_len, idx = record_with_drum(240_000, control)
        self.assertTrue(loop_len == idx)
        self.assertTrue(loop_len == control.drum.length)


if __name__ == "__main__":
    unittest.main()
