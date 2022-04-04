import unittest
from unittest import TestCase

from mixer import Mixer


class TestAlsaMixer(TestCase):
    """integration test, volume is saved in file"""

    def test_1(self):
        mixer1 = Mixer()
        mixer1.setvolume(33, out=True)
        mixer1.setvolume(23, out=False)

        mixer2 = Mixer()
        self.assertEqual(mixer2.getvolume(out=True), 33)
        self.assertEqual(mixer2.getvolume(out=False), 23)

        mixer2.change_volume(65, out=True)
        mixer2.change_volume(10, out=False)

        mixer3 = Mixer()
        self.assertEqual(mixer3.getvolume(out=True), 98)
        self.assertEqual(mixer3.getvolume(out=False), 33)


if __name__ == "__main__":
    unittest.main()
