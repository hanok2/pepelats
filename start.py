import logging
import os
import sys
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

import mido

from loop import ExtendedCtrl
from midi import MidiController, MidiConverter
from screen import ScreenUpdater
from utils import ConfigName
from utils import open_midi_ports


def open_in():
    if ConfigName.use_typing in sys.argv or not os.name == "posix":
        from midi import KbdMidiPort

        return KbdMidiPort()
    else:
        tmp = os.getenv(ConfigName.midi_port_names)
        return open_midi_ports(tmp, is_input=True)


def open_out():
    if ConfigName.use_typing in sys.argv or not os.name == "posix":
        # on Windows need loopmidi application to create this port
        return open_midi_ports(ConfigName.pedal_commands, is_input=False)
    else:
        # on Linix create port form python
        # noinspection PyUnresolvedReferences
        return mido.open_output(ConfigName.pedal_commands, virtual=True)


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

    out_port = open_out()
    in_port = open_in()

    if not in_port or not out_port:
        logging.error(f"MIDI conection failed: {in_port} {out_port}")
        sys.exit(1)

    logging.info(f"MIDI connected: {in_port} {out_port}")
    converter = MidiConverter(in_port, out_port)
    converter.start()

    in_port2 = open_midi_ports(ConfigName.pedal_commands, is_input=True)
    MidiController(s_ctrl, in_port2).start()


if __name__ == "__main__":
    main()
