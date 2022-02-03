import os
import sys
import time
from multiprocessing.connection import Connection

from loop._looperctrl import LooperCtrl
from loop._loopsimple import LoopWithDrum
from loop._songpart import SongPart
from mixer import Mixer
from utils import IN_CHANNELS, OUT_CHANNELS, val_str, ConfigName, SCR_COLS, CURRENT_VERSION
from utils import run_os_cmd


class ExtendedCtrl(LooperCtrl):
    """added more commands"""
    __mixer: Mixer = Mixer()

    def __init__(self, scr_conn: Connection):
        LooperCtrl.__init__(self)
        self.__scr_conn: Connection = scr_conn

    def _redraw(self, update_method: str, description: str) -> None:
        """used by children to _redraw itself on screen"""
        method = getattr(self, update_method)
        info = method()
        part = self.get_item_now()
        self.__scr_conn.send(
            [ConfigName.redraw, info, description, part.length, self.idx, time.time(), self._go_play.is_set()])

    def _prepare_song(self) -> None:
        super()._prepare_song()
        self.items.append(SongPart(self))
        self.items.append(SongPart(self))
        self.items.append(SongPart(self))
        self.items.append(SongPart(self))

    #  ========= change methods

    def _load_drum_type(self):
        self.drum.load_drum_type()

    @staticmethod
    def _change_mixer_volume(*params) -> None:
        out_vol: bool = params[1] == "out"
        ExtendedCtrl.__mixer.change_volume(params[0], out_vol)

    def _change_drum_param(self, *params) -> None:
        if params[1] == "volume":
            self.drum.change_drum_volume(change_by=params[0])
        elif params[1] == "swing":
            self.drum.change_swing(change_by=params[0])
        else:
            raise ValueError("Looper message drum_param has incorrect parameter: " + params[1])

    def _change_drum(self) -> None:
        self.drum.play_ending_now()

    def _change_song(self, *params) -> None:
        self._file_finder.iterate_dir(go_fwd=params[0] > 0)

    def _change_drum_type(self, *params) -> None:
        self.drum.change_drum_type(go_fwd=params[0] >= 0)

    def _change_drum_intensity(self) -> None:
        self.drum.set_next_intensity()

    def _silence_drum(self) -> None:
        self.drum.silence_drum()

    # ================ show methods

    def _show_song(self) -> str:
        ff = self._file_finder
        return f"  now  {ff.get_item_now()}\n  next {ff.get_item_next()}"

    def _show_drum_type(self) -> str:
        return self.drum.show_drum_type()

    def _show_one_part(self) -> str:
        return self.get_item_now().info_str()

    def _show_all_parts(self) -> str:
        tmp = ""
        for part in self.items:
            tmp += part.state_str(self) + LoopWithDrum.info_str(part) + "\n"
        return tmp + f"  Song: {self._song_name}"

    def _show_drum_param(self) -> str:
        tmp = val_str(self.drum.volume, 0, 1, SCR_COLS) + "\n"
        tmp += val_str(self.drum.swing, 0.5, 0.75, SCR_COLS)
        return tmp

    @staticmethod
    def _show_mixer_volume() -> str:
        tmp = val_str(ExtendedCtrl.__mixer.getvolume(out=True), 0, 100, SCR_COLS) + "\n"
        tmp += val_str(ExtendedCtrl.__mixer.getvolume(out=False), 0, 100, SCR_COLS) + "\n"
        tmp += f"  ALSA channels in={IN_CHANNELS} out={OUT_CHANNELS}"
        return tmp

    @staticmethod
    def _show_version() -> str:
        tmp = sys.argv
        return f"  Ver: {CURRENT_VERSION}  args: {tmp}"

    # ================ other methods

    def _fade_and_stop(self, *params):
        self._go_play.clear()
        seconds: int = params[0]
        ExtendedCtrl.__mixer.fade(seconds)
        self.stop_now()

    @staticmethod
    def _restart() -> None:
        ppid = os.getppid()
        run_os_cmd(["kill", "-9", str(ppid)])

    @staticmethod
    def _check_updates() -> None:
        run_os_cmd(["git", "reset", "--hard"])
        if 0 == run_os_cmd(["git", "pull", "--ff-only"]):
            ExtendedCtrl._restart()

    #  ============ All song parts view and related commands

    def _clear_part_id(self, part_id: int) -> None:
        self.is_rec = False
        part = self.items[part_id]
        self.next = self.now
        self._stop_never()
        if not part.is_empty:
            self.items[part_id] = SongPart(self)

    def _undo_part(self) -> None:
        self.is_rec = False
        self.get_item_now().undo()

    def _redo_part(self) -> None:
        self.is_rec = False
        self.get_item_now().redo()

    #  ================= One song part view and related commands

    def _change_loop(self, *params) -> None:
        if self.is_rec:
            return
        part = self.get_item_now()
        if params[0] == "add":
            part.items.append(LoopWithDrum(self, part.length))
            part.now = part.next = part.items_len - 1
            self.is_rec = True
        elif params[0] == "change":
            new_id = part.now + params[1]
            new_id %= part.items_len
            part.now = new_id
        elif params[0] == "delete" and part.now != 0:
            part.items.pop(part.now)
            part.now = 0
        elif params[0] == "silent" and part.now != 0:
            loop = self.get_item_now().get_item_now()
            loop.is_silent = not loop.is_silent
        elif params[0] == "reverse" and part.now != 0:
            loop = self.get_item_now().get_item_now()
            loop.is_reverse = not loop.is_reverse
            loop.is_silent = False
        elif params[0] == "move" and part.now != 0:
            loop = part.items.pop(part.now)
            part.items.append(loop)
            part.now = part.next = part.items_len - 1

    def _undo_loop(self):
        self.is_rec = False
        loop = self.get_item_now().get_item_now()
        loop.undo()

    def _redo_loop(self):
        self.is_rec = False
        loop = self.get_item_now().get_item_now()
        loop.redo()


if __name__ == "__main__":
    pass
