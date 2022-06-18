import logging
import os
import sys
import time
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from threading import Thread

import mido

from loop import ExtendedCtrl
from midi import MidiController
from midi import MidiConverter
from screen import ScreenUpdater
from utils import ConfigName
from utils import open_midi_ports


# noinspection PyUnresolvedReferences
def start_midi():
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


def proc_ctrl(r_conn: Connection, s_conn: Connection):
    pepelats = ExtendedCtrl(s_conn)
    pepelats.start()
    while True:
        msg = r_conn.recv()
        pepelats.process_message(msg)


def proc_updater(r_conn: Connection):
    screen_updater = ScreenUpdater()
    screen_updater.start()
    while True:
        msg = r_conn.recv()
        screen_updater.process_message(msg)


def main():
    r_upd, s_upd = Pipe(False)  # screen update messages
    r_ctrl, s_ctrl = Pipe(False)  # looper control messages

    p_upd = Process(target=proc_updater, args=(r_upd,), daemon=True)
    p_ctrl = Process(target=proc_ctrl, args=(r_ctrl, s_upd), daemon=True)

    p_upd.start()
    p_ctrl.start()

    Thread(target=start_midi, daemon=True).start()
    time.sleep(2)

    in_midi_port = open_midi_ports(ConfigName.pedal_commands, is_input=True)

    MidiController(s_ctrl, in_midi_port).start()


if __name__ == "__main__":
    main()
