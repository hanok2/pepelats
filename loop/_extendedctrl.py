import copy
import os
from multiprocessing.connection import Connection

from loop._looperctrl import LooperCtrl
from loop._songpart import SongPart
from mixer import Mixer
from utils import run_os_cmd
from utils import val_str, ConfigName, SCR_COLS, CURRENT_VERSION, STATE_COLS

USE_COLS = SCR_COLS - STATE_COLS


class ExtendedCtrl(LooperCtrl):
    """Add screen connection and Mixer.
     Add looper commands"""
    __mixer: Mixer = Mixer()

    def __init__(self, scr_conn: Connection):
        LooperCtrl.__init__(self)
        self.__update_method: str = ""
        self.__description: str = ""
        self.__scr_conn: Connection = scr_conn

    def _redraw(self) -> None:
        """used by children to _redraw itself on screen"""
        if self.__update_method:
            method = getattr(self, self.__update_method)
            info = method()
        else:
            info = ""

        part = self.get_item_now()
        self.__scr_conn.send([ConfigName.redraw,
                              info, self.__description, part.length, self.idx,
                              self._go_play.is_set(), self.get_stop_event().is_set()])

    def _prepare_redraw(self, update_method: str, description: str) -> None:
        self.__update_method = update_method
        self.__description = description
        if self._is_rec:
            self._is_rec = False
            part = self.get_item_now()
            loop = part.get_item_now()
            if loop.is_empty:
                loop.trim_buffer(self.idx, self.get_item_now().length)

        self._redraw()

    def _prepare_song(self) -> None:
        super()._prepare_song()
        self.items.append(SongPart(self))
        self.items.append(SongPart(self))
        self.items.append(SongPart(self))
        self.items.append(SongPart(self))

    #  ========= change methods

    def _load_drum_type(self):
        self.drum.load_drum_type()
        self._redraw()

    def _change_mixer_in(self, change_by: int) -> None:
        out_vol: bool = False
        ExtendedCtrl.__mixer.change_volume(change_by, out_vol)
        self._redraw()

    def _change_mixer_out(self, change_by: int) -> None:
        out_vol: bool = True
        ExtendedCtrl.__mixer.change_volume(change_by, out_vol)
        self._redraw()

    def _change_drum_volume(self, change_by: int) -> None:
        self.drum.change_volume(change_by)
        self._redraw()

    def _change_drum_swing(self, change_by: int) -> None:
        self.drum.change_swing(change_by)
        self._redraw()

    def _change_drum(self) -> None:
        self.drum.play_break_now()

    def _change_song(self, *params) -> None:
        self._file_finder.iterate_dir(go_fwd=params[0] > 0)
        self._redraw()

    def _change_drum_type(self, *params) -> None:
        self.drum.change_drum_type(go_fwd=params[0] >= 0)
        self._redraw()

    def _change_drum_intensity(self, change_by: int) -> None:
        self.drum.change_intensity(change_by)

    # ================ show methods

    def _show_song_now(self) -> str:
        ff = self._file_finder
        return ff.get_item_now()

    def _show_song_next(self) -> str:
        ff = self._file_finder
        return ff.get_item_next()

    def _show_drum_type(self) -> str:
        return self.drum.show_drum_type()

    def _show_one_part(self) -> str:
        tmp = ""

        part = self.get_item_now()
        for k, loop in enumerate(part.items):
            tmp += loop.state_str(k == part.now, k == part.next)
            tmp += loop.info_str(USE_COLS)
            tmp += "\n"
        return tmp[:-1]

    def _show_all_parts(self) -> str:
        tmp = ""
        for k, part in enumerate(self.items):
            tmp += part.state_str(k == self.now, k == self.next)
            tmp += part.items[0].info_str(USE_COLS) if part.items_len else "-" * USE_COLS
            tmp += "\n"
        return tmp[:-1]

    def _show_drum_param(self) -> str:
        tmp = "vol:".ljust(STATE_COLS) + val_str(self.drum.volume, 0, 1, USE_COLS) + "\n"
        tmp += "swing:".ljust(STATE_COLS) + val_str(self.drum.swing, 0.5, 0.75, USE_COLS)
        return tmp

    @staticmethod
    def _show_mixer_volume() -> str:
        tmp = "out:".ljust(STATE_COLS) + val_str(ExtendedCtrl.__mixer.getvolume(out=True), 0, 100, USE_COLS) + "\n"
        tmp += "in:".ljust(STATE_COLS) + val_str(ExtendedCtrl.__mixer.getvolume(out=False), 0, 100, USE_COLS)

        return tmp

    @staticmethod
    def _show_version() -> str:
        return f"Version: {CURRENT_VERSION}"

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
        if part_id != self.now:
            self._is_rec = False
            part = self.items[part_id]
            self.next = self.now
            self._stop_never()
            if not part.is_empty:
                self.items[part_id] = SongPart(self)

        self._redraw()

    def _duplicate_part(self) -> None:
        part = self.get_item_now()
        if part.is_empty:
            return
        for x in self.items:
            if x.is_empty:
                x.items = copy.deepcopy(part.items)
                self._redraw()
                break

    def _undo_part(self) -> None:
        self._is_rec = False
        part = self.get_item_now()
        if part.items_len > 1:
            loop = part.items.pop()
            part.now = part.next = 0
            part.backup.append(loop)

        self._redraw()

    def _redo_part(self) -> None:
        self._is_rec = False
        part = self.get_item_now()
        if len(part.backup) > 0:
            part.items.append(part.backup.pop())

        self._redraw()

    #  ================= One song part view and related commands

    def _change_loop(self, *params) -> None:
        if self._is_rec:
            return
        part = self.get_item_now()
        if params[0] == "prev":
            new_id = part.now - 1
            new_id %= part.items_len
            part.now = new_id
        elif params[0] == "next":
            new_id = part.now + 1
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

        self._redraw()

    def _undo_loop(self):
        self._is_rec = False
        part = self.get_item_now()
        if part.now == 0:
            self._undo_part()
        else:
            loop = part.get_item_now()
            loop.undo()

        self._redraw()

    def _redo_loop(self):
        self._is_rec = False
        part = self.get_item_now()
        if part.now == 0:
            self._redo_part()
        else:
            loop = part.get_item_now()
            loop.redo()

        self._redraw()


if __name__ == "__main__":
    pass
