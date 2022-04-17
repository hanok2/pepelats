import unittest
from pathlib import Path
from unittest import TestCase

from utils import JsonDictLoader, ConfigName


class TestLoader(TestCase):

    def test_1(self):
        loader = JsonDictLoader("./etc/looper_defaults.json")
        file: Path = loader.get_filename()
        self.assertTrue(file.name == "looper_defaults.json")
        note: int = loader.get(ConfigName.kbd_notes, dict()).get("1", None)
        self.assertTrue(note == 60)


if __name__ == "__main__":
    unittest.main()
