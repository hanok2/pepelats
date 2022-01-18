import unittest
from multiprocessing import Pipe
from unittest import TestCase

from midi import MidiTranslator
from utils import ConfigName

r_conn, s_conn = Pipe(False)
translator = MidiTranslator(s_conn)


class TestMidiTranslator(TestCase):
    def test_1(self):
        translator.translate_and_send("60")

        msg1 = r_conn.recv()
        msg2 = r_conn.recv()
        self.assertEqual(msg1, ["_play_part_id", 0])
        self.assertEqual(ConfigName.redraw, msg2[0])
        self.assertFalse(r_conn.poll())

    def test_2(self):
        translator.translate_and_send("96")
        msg1 = r_conn.recv()
        msg2 = r_conn.recv()
        self.assertEqual(msg1, ["_clear_part_id", 1])
        self.assertEqual(ConfigName.redraw, msg2[0])
        self.assertFalse(r_conn.poll())


if __name__ == "__main__":
    unittest.main()
