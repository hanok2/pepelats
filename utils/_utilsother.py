import logging
import os
import subprocess as sp
import time
from pathlib import Path
from typing import Any, List, TypeVar, Generic, Union

T = TypeVar('T')

ROOT_DIR = Path(__file__).parent.parent

logging.basicConfig(level=logging.ERROR, filename=Path(ROOT_DIR, 'log.log'), filemode='a')

IS_LINUX = os.name == "posix"
START_TIME = time.time()
CURRENT_VERSION = 'Jan 2022'

# noinspection PyBroadException
try:
    SCR_COLS, SCR_ROWS = os.get_terminal_size()
except Exception:
    SCR_COLS, SCR_ROWS = 32, 10

STATE_COLS = 6  # columns to show loop state - playing, recording ...


# used with assert to print info
def always_true(*args) -> bool:
    print("{:9.3f}".format(time.time() - START_TIME), *args)
    return True


def print_at(row, col, text=""):
    print("\033[%s;%sH%s" % (row, col, text))


def val_str(val: float, min_val: float, max_val: float, cols: int) -> str:
    fill_str: str = "■"
    assert min_val <= val <= max_val, f"Must be: {min_val} <= {val} <= {max_val}"
    val = round(cols * (val - min_val) / (max_val - min_val))
    return fill_str * val


def clear_screen():
    print_at(0, 0, (' ' * SCR_COLS + '\n') * SCR_ROWS)


def run_os_cmd(cmd_list: list[str]) -> int:
    output = sp.run(cmd_list)
    return output.returncode


class MsgProcessor:

    def process_message(self, msg: List[Any]) -> None:
        assert type(msg) == list and len(msg) > 0
        method_name, *params = msg
        try:
            method = getattr(self, method_name)
            method(*params)
        except Exception as err:
            logging.error(f"{self.__class__.__name__} message {msg} error {err}")


class CollectionOwner(Generic[T]):
    """Class for now (selected), next and list of items.
    It is parent for SongPart and LooperFlex"""

    def __init__(self):
        self.items: List[T] = []
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

    def iterate_dir(self, go_fwd: bool) -> None:
        self.next += 1 if go_fwd else -1
        self.next %= self.items_len


class ConfigName:
    #  midi config related
    default_config: str = "default_config"
    update_method: str = "update_method"
    description: str = "description"
    playing_0: str = "playing_0"
    change_map: str = "_change_map"
    show_all_parts: str = "_show_all_parts"
    #  drum related
    default_pattern: str = "default_pattern"
    comment: str = "comment"
    #  other
    use_keyboard_option: str = "--kbd"
    redraw: str = "_redraw"
    one_process: str = "--one"
    no_converter: str = "--no_converter"
    #  main loader
    drum_swing: str = "DRUM_SWING"
    drum_type: str = "DRUM_TYPE"
    drum_volume: str = "DRUM_VOLUME"
    kbd_notes: str = "KBD_NOTES"
    mapped_notes: str = "MAPPED_NOTES"
    midi_port_names: str = "MIDI_PORT_NAMES"


if __name__ == "__main__":
    pass
