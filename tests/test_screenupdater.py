import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from screen import ScreenUpdater
from utils import ConfigName


class TestScreenUpdater(TestCase):

    def test_1(self):
        updater = ScreenUpdater()
        updater._print = MagicMock()
        updater.start()
        updater.process_message([ConfigName.print, "abc", 2, 1])
        updater._print.assert_called_once_with("abc", 2, 1)


if __name__ == "__main__":
    unittest.main()
