import unittest

from utils import MainLoader, ConfigName


class TestMainLoader(unittest.TestCase):

    def test_1(self):
        val = MainLoader.get(ConfigName.drum_swing, -1)
        self.assertTrue(val > 0)


if __name__ == "__main__":
    unittest.main()
