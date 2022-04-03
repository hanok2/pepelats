from threading import Event

from drum import RealDrum
from utils import MAX_32_INT


class OneLoopCtrl:
    """class with events to control one loop, has playback index"""

    max_late_samples = 5000

    def __init__(self):
        self._is_rec: bool = False
        self.__drum = RealDrum()
        self.idx: int = 0
        self.__stop_len: int = MAX_32_INT
        self.__stop_event: Event = Event()

    @property
    def is_rec(self) -> bool:
        return self._is_rec

    @property
    def drum(self) -> RealDrum:
        return self.__drum

    def is_stop_len_set(self) -> bool:
        return self.__stop_len < MAX_32_INT

    def get_stop_len(self) -> int:
        return self.__stop_len

    def get_stop_event(self) -> Event:
        return self.__stop_event

    def stop_now(self) -> None:
        self.__stop_event.set()

    def _stop_never(self) -> None:
        self.__stop_len = MAX_32_INT

    def _stop_record(self) -> None:
        self._is_rec = False

    def _stop_at_bound(self, bound_value: int) -> None:
        over = self.idx % bound_value
        if over < OneLoopCtrl.max_late_samples:
            self.__stop_event.set()
        else:
            self.__stop_len = self.idx - over + bound_value

    def __str__(self):
        stop = f"stop_len {self.__stop_len}" if self.is_stop_len_set() else "stop_len=None"
        return f"{self.__class__.__name__} {stop} {self.drum}"


if __name__ == "__main__":
    pass
