import logging
import os
import sys

import mido

from midi import MidiConverter
from utils import ConfigName
from utils import open_midi_ports

if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    def main():

        if ConfigName.use_typing in sys.argv or not os.name == "posix":
            from midi import KbdMidiPort

            in_port = KbdMidiPort()
            # on Windows need loopmid application to create this port
            out_port = open_midi_ports(ConfigName.pedal_commands, is_input=False)
        else:
            tmp = os.getenv(ConfigName.midi_port_names)
            in_port = open_midi_ports(tmp, is_input=True)
            # on Linix create port form python
            out_port = mido.open_output(ConfigName.pedal_commands, virtual=True)

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
