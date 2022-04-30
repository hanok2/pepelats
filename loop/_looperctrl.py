from threading import Thread, Event

from loop._loopsimple import LoopWithDrum
from loop._oneloopctrl import OneLoopCtrl
from loop._song import Song
from utils import MsgProcessor, MAX_LEN


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
                if self.is_stop_len_set():
                    self._stop_at_bound(self.drum.length)
                else:
                    self._stop_at_bound(part.length)
                    self.drum.play_break_later(part.length, self.idx)
            else:
                self._stop_never()

    def _set_drum_length(self, length: int) -> None:
        self.drum.prepare_drum(length)

    def _get_drum_length(self) -> int:
        return self.drum.length

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

    def _play_loop_next(self) -> None:
        if not self._go_play.is_set():
            self._go_play.set()
            return

        part = self.get_item_now()
        loop = part.get_item_now()
        loop.is_silent = False
        if self._is_rec:
            self._is_rec = False
        else:
            self._is_rec = True
            loop.save_undo()

        self._redraw()

    def _record_part(self):
        if self.next == self.now and self.is_rec:
            part = self.get_item_now()
            loop = part.get_item_now()
            if not loop.is_empty:
                loop.resize_buff(MAX_LEN)

    def _play_part_id(self, part_id: int) -> None:
        prev = self.next
        self.next = part_id

        if not self._go_play.is_set():
            self._go_play.set()
            self._redraw()
            return

        part = self.get_item_now()
        loop = part.get_item_now()
        if part.now > 0 and self.is_rec and loop.is_empty:
            loop.finalize(self.idx, part.length)

        if prev != part_id and part_id == self.now:
            self._stop_never()
            self._redraw()
            return

        if self.next == self.now:
            if self._is_rec:
                part.backup.clear()
                self._is_rec = False
            else:
                part.items.append(LoopWithDrum(self, part.length))
                part.now = part.next = part.items_len - 1
                self._is_rec = True

        self.__stop_quantized()
        self._redraw()


if __name__ == "__main__":
    pass
