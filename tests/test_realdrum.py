import unittest

from drum import RealDrum

drum = RealDrum()


class TestRealDrum(unittest.TestCase):

    def test_1(self):
        """prepare and print"""
        drum.prepare_drum(150_000)
        drum.play_ending_now()
        drum.play_ending_later(1000, 100)
        print(drum)


if __name__ == "__main__":
    unittest.main()
