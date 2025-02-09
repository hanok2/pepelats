import time
import unittest
from multiprocessing.connection import Pipe
from typing import Dict
from unittest import TestCase

import mido

r_conn, s_conn = Pipe(False)


class EndOfTest(Exception):
    pass


class MockOutMidiPort:
    def send(self, msg: mido.Message) -> None:
        pass


class MockInMidiPort:
    def __init__(self):
        self.__notes: Dict[float, int] = dict()

    def charge(self, notes: Dict[float, int]):
        """set dictionary of {time: note, ...} to send e.g. {0.1: 60, 0.2: -60, 1.2:62}
        negative values are note off messages"""
        self.__notes.clear()
        for k, v in notes.items():
            if v >= 0:
                self.__notes[k] = mido.Message.from_bytes([0x90, v, 100])
            else:
                self.__notes[k] = mido.Message.from_bytes([0x80, -v, 0])

    def receive(self) -> mido.Message:
        if len(self.__notes) == 0:
            raise EndOfTest()

        k = list(self.__notes)[0]
        time.sleep(k)
        return self.__notes.pop(k)

    def receive1(self) -> mido.Message:
        if len(self.__notes) == 0:
            raise EndOfTest()

        k = list(self.__notes)[0]
        time.sleep(k)
        return self.__notes.pop(k)


class TestMidiConverter(TestCase):

    def test_1(self):
        pass


if __name__ == "__main__":
    unittest.main()
