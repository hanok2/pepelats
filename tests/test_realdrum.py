import unittest

from drum import RealDrum, DrumLoader

drum = RealDrum()


class TestRealDrum(unittest.TestCase):

    def test_1(self):
        """prepare and print"""
        DrumLoader.prepare_all(150_000)

        drum.play_ending_now()
        print(drum)


if __name__ == "__main__":
    unittest.main()
