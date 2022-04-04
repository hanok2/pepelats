import unittest
from pathlib import Path
from unittest import TestCase

from utils import JsonDictLoader, ConfigName


class TestLoader(TestCase):

    def test_1(self):
        loader = JsonDictLoader("./etc/count/kbd_notes.json")
        file: Path = loader.get_filename()
        self.assertTrue(file.name == "kbd_notes.json")
        note: int = loader.get(ConfigName.kbd_notes, dict()).get("1", None)
        self.assertTrue(note == 60)

    def test_2(self):
        loader = JsonDictLoader("./etc/count/mapped_notes.json")
        file: Path = loader.get_filename()
        self.assertTrue(file.name == "mapped_notes.json")
        note: int = loader.get(ConfigName.mapped_notes, dict()).get("60", None)
        self.assertTrue(note == 80)


if __name__ == "__main__":
    unittest.main()
