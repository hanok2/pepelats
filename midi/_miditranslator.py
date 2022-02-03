from multiprocessing.connection import Connection

from midi._midiconfigloader import MidiConfigLoader
from utils import ConfigName, always_true


class MidiTranslator:
    """Translate note to command with parameters and sends to a connection"""

    def __init__(self, s_conn: Connection):
        self.__s_conn = s_conn

    def translate_and_send(self, note: str) -> None:
        msg = MidiConfigLoader.get(note)
        if msg is not None:
            method_name, *params = msg
            assert always_true(f"Sending message: {msg}")
            if method_name == ConfigName.change_map:
                MidiConfigLoader.change_map(params[0])
            else:
                self.__s_conn.send(msg)
            update_method = MidiConfigLoader.get(ConfigName.update_method)
            description = MidiConfigLoader.get(ConfigName.description)
            msg = [ConfigName.redraw, update_method, description]
            assert always_true(f"Sending message: {msg}")
            self.__s_conn.send(msg)
