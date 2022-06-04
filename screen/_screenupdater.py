import os
import sys
import time
from threading import Thread
from typing import Tuple

from utils import SCR_COLS, print_at, MsgProcessor, SD_RATE, SCR_ROWS

UPDATES_PER_LOOP = 8


def extend_strings(s: str, fill_char: str, cols: int) -> Tuple[str, int]:
    line_list = s.split('\n')
    mp = map(lambda x: x.ljust(cols, fill_char), line_list)
    return "\n".join(list(mp)), len(line_list) + 1


class ScreenUpdater(MsgProcessor):
    def __init__(self):
        super().__init__()
        self.__stop: bool = True
        self.__delta: float = 1000000
        self.__sleep_time: float = 1
        self.__loop_len: int = 1000000
        self.__idx: int = 0
        self.__description: str = ""  # keep latest one
        self.__t1: Thread = Thread(target=self.__progress_update, name="progress_update_thread", daemon=True)

    def start(self):
        self.__t1.start()

    def _print(self, info: str, description: str, loop_len: int, idx: int, stop: bool) -> None:
        self.__stop = stop
        self.__delta = loop_len / UPDATES_PER_LOOP
        self.__sleep_time = self.__delta / SD_RATE
        self.__loop_len = loop_len
        if description:
            self.__description = description
        self.__idx = idx
        if not __debug__:
            # clear all if NOT debug
            print_at(2, 1, ' ' * (SCR_ROWS - 1) * SCR_COLS)
        print_at(2, 1, info)
        print(self.__description)

    def __progress_update(self):
        if os.name != "posix":
            return

        while True:
            time.sleep(self.__sleep_time)
            if not self.__stop:
                self.__idx += self.__delta
                self.__idx %= self.__loop_len
                pos = round(self.__idx / self.__loop_len * SCR_COLS)
                # cursor position starts at 1,1
                print_at(1, 1, "■" * pos + " " * (SCR_COLS - pos))
                sys.stdout.flush()


if __name__ == "__main__":
    pass
