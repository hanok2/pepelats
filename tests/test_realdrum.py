import time
import unittest

from drum import RealDrum

drum = RealDrum()


class TestDrumSound(unittest.TestCase):

    def test_1(self):
        """prepare and print"""
        drum.prepare_drum(150_000)
        print(drum)

        while drum.is_silent:
            time.sleep(0.1)
        drum.sound_test(1, False)
        print(drum)


if __name__ == "__main__":
    unittest.main()
