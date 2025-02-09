from multiprocessing.connection import Connection

from midi._miditranslator import MidiTranslator
from utils import always_true


class MidiController:

    def __init__(self, s_conn: Connection, in_port):

        self._translator: MidiTranslator = MidiTranslator(s_conn)
        self.__in_port = in_port

    def start(self) -> None:
        assert always_true("Started MidiController")
        while True:
            msg = self.__in_port.receive()
            if msg is None:
                continue
            note = msg.bytes()[1]
            self._translator.translate_and_send(str(note))

    def __str__(self):
        return f"{self.__class__.__name__}"


if __name__ == "__main__":
    pass
