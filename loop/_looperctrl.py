from abc import abstractmethod
from threading import Thread, Event

from loop._loopsimple import LoopWithDrum
from loop._oneloopctrl import OneLoopCtrl
from loop._song import Song
from utils import MsgProcessor, ConfigName, clear_screen


class LooperCtrl(Song, MsgProcessor):
    """added playback thread, message thread via MsgListener.
     Song is collection of song parts with related methods"""

    def __init__(self):
        self._go_play = Event()
        OneLoopCtrl.__init__(self)
        MsgProcessor.__init__(self)
        Song.__init__(self)
        self.__t1: Thread = Thread(target=self.__playback, name="playback_thread", daemon=True)

    def start(self):
        self.__t1.start()
        clear_screen()
        self._redraw(ConfigName.show_all_parts, "")

    def set_drum_length(self, length: int) -> None:
        if length > 0:
            self.drum.prepare_drum(length)

    def get_drum_length(self) -> int:
        return self.drum.length

    @abstractmethod
    def _redraw(self, update_method: str, description: str) -> None:
        """used by children to _redraw itself on screen"""
        pass

    def _prepare_song(self) -> None:
        self._stop_song()
        self.items.clear()
        self.drum.clear()

    def _stop_song(self):
        self.is_rec = False
        self._go_play.clear()
        self.stop_now()

    def _pause_and_clear(self) -> None:
        if self._go_play.is_set():
            self._go_play.clear()
            self._stop_at_bound(self.get_item_now().length)
        else:
            self._prepare_song()

    def _play_loop_next(self) -> None:
        if not self._go_play.is_set():
            self._go_play.set()
            return

        part = self.get_item_now()
        loop = part.get_item_now()
        loop.is_silent = False
        if not self.is_rec:
            if part.now == 0:
                part.items.append(LoopWithDrum(self))
                part.now = part.next = part.items_len - 1
            else:
                loop.save_undo()
        else:
            if loop.is_empty:
                loop.trim_buffer(self.idx, self.get_item_now().length)

        self.is_rec = not self.is_rec

    def _play_part_id(self, part_id: int) -> None:
        if not self._go_play.is_set():
            self._go_play.set()
        self.next = part_id
        if self.next == self.now:
            if not self.is_rec:
                self.get_item_now().save_undo()
            self.is_rec = not self.is_rec
        self.__stop_quantized()

    def __playback(self) -> None:
        """runs in a thread, play and record current song part"""
        while True:
            self._go_play.wait()
            if self.next != self.now:
                self.now = self.next

            part = self.get_item_now()
            self.get_stop_event().clear()
            self._stop_never()
            self.idx = 0
            self.is_rec = part.is_empty
            self._redraw(ConfigName.show_all_parts, "")
            part.play_buffer()

    def __stop_quantized(self) -> None:
        """the method for quantized playback and recording,
        has logic when to stop playback"""
        part = self.get_item_now()
        if part.is_empty:
            if self.drum.is_empty:
                self.stop_now()
            else:
                self._stop_at_bound(self.drum.length)
        else:
            if self.next != self.now:
                if self.is_stop_len_set():
                    self._stop_at_bound(self.drum.length)
                else:
                    self._stop_at_bound(part.length)
                    self.drum.play_ending_later(part.length, self.idx)
            else:
                self._stop_never()


if __name__ == "__main__":
    pass
