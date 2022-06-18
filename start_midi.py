import json
import logging
import os
import sys
from typing import List

import mido

from midi import MidiConverter
from utils import ConfigName


# noinspection PyUnresolvedReferences
def open_midi_ports(port_names_str: str, is_input: bool):
    try:
        port_names: List[str] = json.loads("[" + port_names_str + "]")
    except Exception as ex:
        logging.error(f"Failed to parse port names, error: {ex}\nstring value: {port_names_str}")
        sys.exit(1)

    port_list = mido.get_input_names() if is_input else mido.get_output_names()
    for name in port_names:
        for port_name in port_list:
            if name in port_name:
                print(f"opening: {port_name} input: {is_input}")
                if is_input:
                    return mido.open_input(port_name)
                else:
                    return mido.open_output(port_name)


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    def main():

        if ConfigName.use_typing in sys.argv or not os.name == "posix":
            from midi import KbdMidiPort

            in_port = KbdMidiPort()
            # on Windows need loopmid application to create this port
            out_port = open_midi_ports('"pedalCmd"', is_input=False)
        else:
            tmp = os.getenv(ConfigName.midi_port_names)
            in_port = open_midi_ports(tmp, is_input=True)
            # on Linix create port form python
            out_port = mido.open_output("pedalCmd", virtual=True)

        if not in_port:
            logging.error("Failed to connecting to MIDI input")
            sys.exit(1)

        if not out_port:
            logging.error("Failed to connecting to MIDI output")
            sys.exit(1)

        logging.info(f"Connected to MIDI input: {in_port.name} output: {out_port.name}")
        converter = MidiConverter(in_port, out_port)

        converter.start()


    main()
