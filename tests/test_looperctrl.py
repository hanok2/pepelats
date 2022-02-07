import unittest
from multiprocessing import Pipe
from unittest.mock import MagicMock

# noinspection PyProtectedMember
from loop._looperctrl import LooperCtrl

r_conn, s_conn = Pipe(False)


class TestLooperCtrl(unittest.TestCase):

    def test_1(self):
        control = LooperCtrl()
        control._play_part_id = MagicMock()
        control._redraw = MagicMock()
        control.start()
        control.process_message(["_play_part_id", 123])

        control._play_part_id.assert_called_once_with(123)


if __name__ == "__main__":
    unittest.main()
