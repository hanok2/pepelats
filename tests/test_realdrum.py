import unittest

from drum import RealDrum

drum = RealDrum()


class TestDrumSound(unittest.TestCase):

    def test_1(self):
        """prepare and print"""
        drum.prepare_drum_blocking(150_000)
        print(drum)

        drum.sound_test(1, False)
        print(drum)


if __name__ == "__main__":
    unittest.main()
