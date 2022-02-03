import unittest
from unittest.mock import MagicMock

from midi import ScreenUpdater
from utils import ConfigName


class TestScreenUpdater(unittest.TestCase):

    def test_1(self):
        updater = ScreenUpdater()
        updater._redraw = MagicMock()
        updater.start()
        updater.process_message([ConfigName.redraw, "abc", 2, 1])
        updater._redraw.assert_called_once_with("abc", 2, 1)


if __name__ == "__main__":
    unittest.main()
