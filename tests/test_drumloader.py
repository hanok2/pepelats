import unittest

from drum import DrumLoader
from utils import FileFinder, ConfigName, MainLoader, sound_test


class TestDrumLoader(unittest.TestCase):

    def test_1(self):
        """Does actual load of drums"""
        ff = FileFinder("etc/drums", False, "", MainLoader.get(ConfigName.drum_type, "pop"))
        for _ in range(ff.items_len):
            ff.iterate_dir(True)
            ff.now = ff.next
            tmp = ff.get_path_now()
            print(tmp)
            DrumLoader.load(tmp)
            DrumLoader.prepare_all(150_000)
            sound_test(DrumLoader.patterns[0], 1, False)
            print(DrumLoader.to_str())


if __name__ == "__main__":
    unittest.main()
