import sys
from time import sleep
from typing import List

import mido

from utils._utilsloader import MainLoader
from utils._utilsother import ConfigName, IS_LINUX


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
            sleep(5)

    if ConfigName.use_keyboard_option in sys.argv or not IS_LINUX:
        from midi import KbdMidiPort
        tmp = MainLoader.get(ConfigName.kbd_notes, dict())
        return KbdMidiPort(tmp)
    else:
        tmp = MainLoader.get(ConfigName.midi_port_names, [])
        return wait_for_midi_ports(tmp)
