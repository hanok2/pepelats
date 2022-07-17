import logging
import os
import subprocess as sp
import time
import traceback
from datetime import datetime
from math import log10
from pathlib import Path
from typing import Any, List, TypeVar, Generic, Union, Dict

T = TypeVar('T')

ROOT_DIR = Path(__file__).parent.parent

logging.basicConfig(level=logging.INFO, filename=Path(ROOT_DIR, 'log.log'), filemode='a')
logging.getLogger().addHandler(logging.StreamHandler())
logging.info(f"Starting log: {datetime.now()}")

START_TIME = time.time()
CURRENT_VERSION = 'June 2022'

# noinspection PyBroadException
try:
    SCR_COLS, SCR_ROWS = os.get_terminal_size()
except Exception:
    SCR_COLS, SCR_ROWS = 32, 10

STATE_COLS = 6  # columns to show loop state - playing, recording ...

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


# used with assert to print info
def always_true(*args) -> bool:
    print("{:9.3f}".format(time.time() - START_TIME), *args)
    return True


def print_at(row, col, text=""):
    print("\033[%s;%sH%s" % (row, col, text))


def val_str(val: float, min_val: float, max_val: float, cols: int) -> str:
    assert min_val <= val <= max_val, f"Must be: {min_val} <= {val} <= {max_val}"
    assert min_val < max_val, f"Must be: {min_val} < {max_val}"
    k = round(cols * (val - min_val) / (max_val - min_val))
    k = min(k, cols - 1)
    return ('-' * k + '╬').ljust(cols, '-')


def decibels(val_ratio: float) -> float:
    """calculate decibels from -60 to 0"""
    db = 20 * log10(val_ratio)
    db = max(db, -60)
    return db


def run_os_cmd(cmd_list: list[str]) -> int:
    if os.name != "posix":
        return 1
    output = sp.run(cmd_list)
    return output.returncode


class MsgProcessor:

    def fake(self):
        pass

    def process_message(self, msg: List[Any]) -> None:
        assert type(msg) == list and len(msg) > 0
        method_name, *params = msg
        found_method = False
        try:
            method = getattr(self, method_name)
            found_method = True
            method(*params)
        except Exception as err:
            logging.error(f"{self.__class__.__name__} got message: {msg}, "
                          f"got error: {err}, found method: {found_method}, info: {traceback.format_exc()}")


class CollectionOwner(Generic[T]):
    """Class for now (selected), next and list of items.
    It is parent for SongPart and LooperFlex"""

    def __init__(self):
        self.items: List[T] = []
        self.backup: List[T] = []
        self.now: int = 0
        self.next: int = 0

    def get_item_now(self) -> T:
        return self.items[self.now]

    def get_item_next(self) -> T:
        return self.items[self.next]

    @property
    def items_len(self):
        return len(self.items)


class FileFinder(CollectionOwner[str]):
    def __init__(self, dir_name: Union[str, Path], is_file: bool, end_with: str, initial: str):
        super().__init__()
        self.__end_with = end_with
        self.__dir_name = Path(ROOT_DIR, dir_name)
        self.__dir_name.mkdir(parents=True, exist_ok=True)

        def chk_file(d, f):
            return os.path.isfile(os.path.join(d, f))

        self.items = [p for p in os.listdir(self.__dir_name)
                      if is_file == chk_file(self.__dir_name, p)
                      and p.endswith(self.__end_with)]

        if initial and initial in self.items:
            self.now = self.items.index(initial)

    def get_dir_name(self) -> Path:
        return self.__dir_name

    def get_path_now(self) -> Path:
        return Path(self.__dir_name, self.get_item_now())

    def get_end_with(self) -> str:
        return self.__end_with

    def iterate_dir(self, go_fwd: bool) -> None:
        self.next += 1 if go_fwd else -1
        self.next %= self.items_len


class ConfigName:
    #  midi config related
    default_config: str = "default_config"
    update_method: str = "update_method"
    description: str = "description"
    playing: str = "playing"
    change_map: str = "_change_map"
    show_all_parts: str = "_show_all_parts"
    #  drum related
    default_pattern: str = "default_pattern"
    comment: str = "comment"
    #  other
    use_typing: str = "--use_typing"
    # redraw
    prepare_redraw: str = "_prepare_redraw"
    redraw: str = "_redraw"
    print: str = "_print"
    #  main loader
    drum_swing: str = "DRUM_SWING"
    drum_type: str = "DRUM_TYPE"
    drum_volume: str = "DRUM_VOLUME"
    usb_audio_names: str = "USB_AUDIO_NAMES"
    max_late_seconds: str = "MAX_LATE_SECONDS"
    port_name = "Pepelats"


if __name__ == "__main__":
    pass
