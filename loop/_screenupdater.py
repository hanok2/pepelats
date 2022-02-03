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
        count1 = info.count('\n')
        print_at(2, 0, info)
        count2 = len(description)
        print(description)
        count = SCR_ROWS - (count1 + 1)
        count = count * SCR_COLS - count2
        print('.' * count)

    def __progress_update(self):
        while True:
            time.sleep(self.__sleep_time)
            if self.__is_play:
                self.__idx += self.__delta
                self.__idx %= self.__loop_len
                pos = round(self.__idx / self.__loop_len * SCR_COLS)
                print_at(0, 0, "■" * pos + " " * (SCR_COLS - pos))


if __name__ == "__main__":
    pass
