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

        msg = r_conn.recv()
        if msg[0] == ConfigName.prepare_redraw:
            msg = r_conn.recv()
        self.assertEqual(msg, ["_play_part_id", 0])
        self.assertFalse(r_conn.poll())

    def test_2(self):
        translator.translate_and_send("96")
        msg = r_conn.recv()
        if msg[0] == ConfigName.prepare_redraw:
            msg = r_conn.recv()
        self.assertEqual(msg, ["_clear_part_id", 1])
        self.assertFalse(r_conn.poll())


if __name__ == "__main__":
    unittest.main()
