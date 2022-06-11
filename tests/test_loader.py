import unittest
from pathlib import Path
from unittest import TestCase

from utils import JsonDictLoader, ConfigName


class TestLoader(TestCase):

    def test_1(self):
        loader = JsonDictLoader("./etc/looper_defaults.json")
        file: Path = loader.get_filename()
        self.assertTrue(file.name == "looper_defaults.json")
        swing: float = loader.get(ConfigName.drum_swing, -1)
        self.assertTrue(swing >= 0.5)


if __name__ == "__main__":
    unittest.main()
