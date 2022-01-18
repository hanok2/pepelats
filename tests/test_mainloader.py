import unittest

from utils import MainLoader


class TestMainLoader(unittest.TestCase):

    def test_1(self):
        MainLoader.set("TEST", 232)
        val = MainLoader.get("TEST", -1)
        self.assertEqual(val, 232)

    def test_2(self):
        MainLoader.set("TEST", 232)
        val = MainLoader.get("TEST", -1)
        self.assertEqual(val, 232)


if __name__ == "__main__":
    unittest.main()
