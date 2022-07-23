import os
import sys
import time
from threading import Thread

import mido

from utils import SCR_COLS, print_at, MsgProcessor, SD_RATE, SCR_ROWS

UPDATES_PER_LOOP = 16
CLOCKS_PER_BAR = 96
MIDI_CLOCK = mido.Message.from_bytes([0xF8])
MIDI_START = mido.Message.from_bytes([0xFA])
MIDI_STOP = mido.Message.from_bytes([0xFC])


class ScreenUpdater(MsgProcessor):
    def __init__(self):
        super().__init__()
        port_name = os.getenv("LOOPER_CLOCK_NAME", "LooperClock_out")
        # noinspection PyUnresolvedReferences
        self.__out_midi = mido.open_output(port_name)
        self.__stop: bool = True
        self.__delta: float = 1000000
        self.__sleep_time: float = 1
        self.__loop_len: int = 1000000
        self.__idx: int = 0
        self.__count = 0
        self.__countTo = 0
        self.__t1: Thread = Thread(target=self.__progress_update, name="progress_update_thread", daemon=True)

    def start(self):
        self.__t1.start()

    def _print(self, info: str, description: str, drum_len: int, loop_len: int, idx: int, stop: bool) -> None:
        self.__stop = stop
        self.__count = 0
        self.__delta = loop_len // UPDATES_PER_LOOP
        self.__loop_len = loop_len
        self.__idx = idx

        if not self.__out_midi or not drum_len:
            self.__countTo = 1
            self.__sleep_time = loop_len / UPDATES_PER_LOOP / SD_RATE
        else:
            if self.__stop:
                self.__out_midi.send(MIDI_STOP)
            else:
                self.__out_midi.send(MIDI_START)
            self.__countTo = loop_len / drum_len * CLOCKS_PER_BAR / UPDATES_PER_LOOP
            self.__sleep_time = drum_len / CLOCKS_PER_BAR / SD_RATE

        if not __debug__:
            # clear all if NOT debug
            print_at(2, 1, ' ' * (SCR_ROWS - 1) * SCR_COLS)
        print_at(2, 1, info)
        print(description)

    def __progress_update(self):
        while True:
            time.sleep(self.__sleep_time)
            progress = not self.__stop
            if self.__out_midi:
                self.__out_midi.send(MIDI_CLOCK)
                progress = progress and self.__count == 0
                self.__count += 1
                if self.__count >= self.__countTo:
                    self.__count = 0

            if progress:
                self.__idx += self.__delta
                self.__idx %= self.__loop_len
                pos = round(self.__idx / self.__loop_len * SCR_COLS)
                # cursor position starts at 1,1
                print_at(1, 1, "■" * pos + " " * (SCR_COLS - pos))
                sys.stdout.flush()


if __name__ == "__main__":
    pass
