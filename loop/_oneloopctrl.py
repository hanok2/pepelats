from threading import Event

from drum import RealDrum, FakeDrum
from utils import MAX_32_INT, ConfigName, MainLoader, SD_RATE


class OneLoopCtrl:
    """class with events to control one loop, has playback index"""

    max_late_samples = MainLoader.get(ConfigName.max_late_seconds, 0.1) * SD_RATE

    def __init__(self):
        self._is_rec: bool = False
        self._drum: FakeDrum = RealDrum()
        self.idx: int = 0
        self.__stop_len: int = MAX_32_INT
        self.__stop_event: Event = Event()

    @property
    def is_rec(self) -> bool:
        return self._is_rec

    @property
    def drum(self) -> FakeDrum:
        return self._drum

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

    def _stop_at_bound(self, bound_value: int) -> None:
        over = self.idx % bound_value
        if over < OneLoopCtrl.max_late_samples:
            self.__stop_event.set()
        else:
            self.__stop_len = self.idx - over + bound_value

    def __str__(self):
        return f"{self.__class__.__name__} stop_len {self.__stop_len} {self._drum} is_rec {self.is_rec}"


if __name__ == "__main__":
    pass
