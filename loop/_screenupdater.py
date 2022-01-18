import time
from threading import Thread
from typing import Dict

from utils import SCR_COLS, print_at, MsgProcessor, SD_RATE

UPDATES_PER_LOOP = 8

# foreground, background ends with '40m'
ScrColors: Dict[str, str] = {
    'b': '\x1b[1;30m',
    'r': '\x1b[1;31m',
    'g': '\x1b[1;32m',
    'y': '\x1b[1;33m',
    'v': '\x1b[1;34m',
    'w': '\x1b[37m',
    'end': '\x1b[0m',
    'reverse': '\x1b[7m'
}


def extend_strings(some_str: str, cols: int) -> str:
    delim: str = '\n'
    mp = map(lambda x: x.ljust(cols), some_str.split(delim))
    return delim.join(list(mp))


def extend_strings_color(some_str: str, cols: int) -> str:
    delim: str = '\n'
    cend = ScrColors['end']
    mp = map(lambda x: x.ljust(cols), some_str.split(delim))
    ls = [ScrColors.get(s[0], '') + s[1:] + cend for s in mp]
    return delim.join(ls)


class ScreenUpdater(MsgProcessor):
    def __init__(self):
        super().__init__()
        self.__is_play: bool = False
        self.__delta: float = 1000000
        self.__sleep_time: float = 1
        self.__loop_len: int = 1000000
        self.__idx: int = 0
        self.__t1: Thread = Thread(target=self.__progress_update, name="progress_update_thread", daemon=True)

    def start(self):
        self.__t1.start()

    def _redraw(self, info: str, description: str, loop_len: int, idx: int, time_stamp: float, is_play: bool) -> None:
        self.__is_play = is_play
        self.__delta = loop_len / UPDATES_PER_LOOP
        self.__sleep_time = self.__delta / SD_RATE
        self.__loop_len = loop_len
        msg_delay = time.time() - time_stamp
        self.__idx = idx + round(msg_delay * SD_RATE)
        print_at(2, 0, extend_strings_color(info, SCR_COLS))
        if description:
            print(extend_strings(description, SCR_COLS))

    def __progress_update(self):
        while True:
            cgreen = ScrColors['g']
            cend = ScrColors['end']
            time.sleep(self.__sleep_time)
            if self.__is_play:
                self.__idx += self.__delta
                self.__idx %= self.__loop_len
                pos = round(self.__idx / self.__loop_len * SCR_COLS)
                print_at(0, 0, cgreen + "■" * pos + " " * (SCR_COLS - pos) + cend)


if __name__ == "__main__":
    pass
