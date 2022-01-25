import sys
import time
from multiprocessing.connection import Connection
from typing import List

import mido

from midi._miditranslator import MidiTranslator
from utils import always_true, ConfigName, IS_LINUX, MainLoader


def get_midi_port():
    """wait for one of MIDI ports for 3 minutes, open and return input port or None"""

    # noinspection PyUnresolvedReferences
    def wait_for_midi_ports(port_names: List[str]):
        for k in range(3):
            print("Waiting for MIDI port to appear:", port_names)
            port_list = mido.get_input_names()
            for name in port_names:
                for port_name in port_list:
                    if name in port_name:
                        print("opening:", port_name)
                        port_in = mido.open_input(port_name)
                        return port_in
            time.sleep(5)

    if ConfigName.use_keyboard_option in sys.argv or not IS_LINUX:
        from midi._kbdmidiport import KbdMidiPort
        tmp = MainLoader.get(ConfigName.kbd_notes, dict())
        return KbdMidiPort(tmp)
    else:
        tmp = MainLoader.get(ConfigName.midi_port_names, [])
        return wait_for_midi_ports(tmp)


class MidiCounter:

    def __init__(self, s_conn: Connection, in_port):

        self.__translator: MidiTranslator = MidiTranslator(s_conn)
        self.__in_port = in_port
        self.__exit_note: int = MainLoader.get(ConfigName.exit_note, 59)
        self.__alive: bool = True

    def start(self) -> None:
        assert always_true("Started MIDI note counter")
        while self.__alive:
            msg = self.__in_port.receive()
            if msg is None:
                continue
            note = msg.bytes()[1]
            self.__translator.translate_and_send(str(note))

    def __str__(self):
        return f"{self.__class__.__name__}"


if __name__ == "__main__":
    pass
