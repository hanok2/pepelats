from threading import Thread, Event

from loop._loopsimple import LoopWithDrum
from loop._oneloopctrl import OneLoopCtrl
from loop._song import Song
from utils import MsgProcessor


class LooperCtrl(OneLoopCtrl, Song, MsgProcessor):
    """added playback thread, MsgProcessor and Song.
     Song is collection of song parts with related methods"""

    def __init__(self):
        self._go_play = Event()
        OneLoopCtrl.__init__(self)
        MsgProcessor.__init__(self)
        Song.__init__(self)
        self.__t1: Thread = Thread(target=self.__playback, name="playback_thread", daemon=True)

    def _get_control(self) -> OneLoopCtrl:
        return self

    def start(self):
        self.__t1.start()

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
            self._is_rec = part.is_empty
            self._redraw()
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
                self._stop_at_bound(part.length)
                self.drum.play_break_later(part.length, self.idx)
            else:
                self._stop_never()

    def _set_drum_length(self, length: int) -> None:
        if length > 0:
            self.drum.prepare_drum(length)

    def _get_drum_length(self) -> int:
        return self.drum.length

    def _redraw(self) -> None:
        """used by children to redraw itself on screen"""
        pass

    def _prepare_song(self) -> None:
        self._stop_song()
        self.items.clear()
        self.drum.clear()

    def _stop_song(self, wait: int = 0):
        self._is_rec = False
        self._go_play.clear()
        if not wait:
            self.stop_now()
        else:
            self._stop_at_bound(self.get_item_now().length)

    def _pause_and_clear(self) -> None:
        if self._go_play.is_set():
            self._go_play.clear()
        else:
            self._prepare_song()

    def _overdub_loop(self) -> None:
        if not self._go_play.is_set():
            self._go_play.set()
            return

        part = self.get_item_now()
        loop = part.get_item_now()
        loop.is_silent = False
        if self._is_rec:
            self._is_rec = False
        else:
            loop.save_undo()
            self._is_rec = True

        self._redraw()

    def _play_part_id(self, part_id: int) -> None:
        self.next = part_id
        self._is_rec = False

        if not self._go_play.is_set():
            self._go_play.set()
            self._redraw()
            return

        self.__stop_quantized()
        self._redraw()

    def _overdub(self) -> None:
        """add recording of same length as initial loop - part.items[0]"""

        if self.next != self.now or self.is_rec:
            return

        part = self.get_item_now()
        part.backup.clear()
        self._is_rec = True
        part.items.append(LoopWithDrum(self, part.items[0].length))
        part.now = part.next = part.items_len - 1

        self._redraw()

    def _record(self) -> None:
        """add recording of unknown length, multiple of drum length or initial loop length"""

        if self.next != self.now or self.is_rec:
            return

        part = self.get_item_now()
        part.backup.clear()
        part.items.append(LoopWithDrum(self))
        part.now = part.next = part.items_len - 1
        part.backup.clear()
        self._is_rec = True

        self._redraw()


if __name__ == "__main__":
    pass
