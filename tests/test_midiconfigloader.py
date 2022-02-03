import unittest

# noinspection PyProtectedMember
from midi._midiconfigloader import MidiConfigLoader


class TestMidiConfigLoader(unittest.TestCase):

    def test_1(self):
        """Does actual load of midi config"""
        msg = MidiConfigLoader.get("60")
        self.assertTrue(type(msg) == list)


if __name__ == "__main__":
    unittest.main()
