import unittest
from unittest import TestCase

from loop import WrapBuffer
from utils import make_sin_sound, SD_RATE, STATE_COLS, SCR_COLS

sound_len = 500_000  # samples
sound = make_sin_sound(440, sound_len / SD_RATE)


class TestWrapBuffer(TestCase):

    def test_1(self):
        test_buff = WrapBuffer()
        test_buff.record_samples(sound[:100_000], 0)
        test_buff.trim_buffer(121_000, -1)
        self.assertTrue(test_buff.length == 121_000)
        print(test_buff.info_str(SCR_COLS - STATE_COLS))
        test_buff.sound_test(1, False)

    def test_trim2(self):
        test_buff = WrapBuffer()
        test_buff.record_samples(sound[:10], 0)
        test_buff.trim_buffer(121_000, 100_000)
        self.assertTrue(test_buff.length == 100_000)

    def test_trim3(self):
        test_buff = WrapBuffer()
        test_buff.record_samples(sound[:10], 0)
        test_buff.trim_buffer(10, 100_000)
        self.assertTrue(test_buff.length == 100_000)

    def test_trim5(self):
        test_buff = WrapBuffer()
        had_error = False
        try:
            test_buff.trim_buffer(151_000, 100_000)
        except AssertionError as err:
            self.assertTrue("without recording" in str(err))
            had_error = True

        self.assertTrue(had_error)


if __name__ == "__main__":
    unittest.main()
