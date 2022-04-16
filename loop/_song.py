import os
import pickle
from abc import abstractmethod
from datetime import datetime

from loop._oneloopctrl import OneLoopCtrl
from loop._songpart import SongPart
from utils import CollectionOwner, FileFinder, always_true


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self):
        super().__init__()
        self._file_finder: FileFinder = FileFinder("save_song", True, ".sng", "")
        self._song_name = ""
        self.__set_song_name()

    @abstractmethod
    def _prepare_song(self) -> None:
        pass

    @abstractmethod
    def _stop_song(self, wait: int = 0) -> None:
        pass

    @abstractmethod
    def _set_drum_length(self, length: int) -> None:
        pass

    @abstractmethod
    def _get_drum_length(self) -> int:
        pass

    @abstractmethod
    def _get_control(self) -> OneLoopCtrl:
        pass

    def _load_song(self) -> None:
        self._stop_song()
        self._file_finder.now = self._file_finder.next
        full_name = self._file_finder.get_path_now()
        assert always_true(f"Loading song file {full_name}")
        with open(full_name, 'rb') as f:
            length, load_list = pickle.load(f)

        self.items.clear()
        ctrl = self._get_control()
        for k in load_list:
            self.items.append(k if k is not None else SongPart(ctrl))

        for a in self.items:
            a._ctrl = ctrl
            for b in a.items:
                b._ctrl = ctrl

        self._set_drum_length(length)

    def _save_song(self) -> None:
        self._stop_song()
        length = self._get_drum_length()
        save_list = []
        for k in self.items:
            save_list.append(k if not k.is_empty else None)

        full_name = self._file_finder.get_path_now()
        assert always_true(f"Saving song file {full_name}")
        with open(full_name, 'wb') as f:
            pickle.dump((length, save_list), f)

    def _save_new_song(self):
        self._song_name = self.__new_song_name()
        self._file_finder.items.append(self._song_name)
        self._file_finder.now = self._file_finder.items_len - 1
        self._save_song()

    def _delete_song(self) -> None:
        self._stop_song()
        self._file_finder.now = self._file_finder.next
        path = self._file_finder.get_path_now()
        if os.path.isfile(path):
            os.remove(path)
        self._file_finder.items.pop(self._file_finder.now)
        self._file_finder.now = self._file_finder.next = 0
        self.__set_song_name()

    def __new_song_name(self) -> str:
        return datetime.now().strftime("%m-%d-%H-%M-%S") + self._file_finder.get_end_with()

    def __set_song_name(self):
        """create empty song or select latest saved song"""
        if self._file_finder.items_len == 0:
            self._prepare_song()
            self._save_new_song()
        elif self._song_name not in self._file_finder.items:
            self._file_finder.now = self._file_finder.items_len - 1
            self._song_name = self._file_finder.get_item_now()
            self._load_song()
        else:
            self._file_finder.now = self._file_finder.items.index(self._song_name)
