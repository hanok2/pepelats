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


def start_midi(out_port):
    in_port = None
    logging.info(f"MIDI output {out_port}")

    while True:
        # noinspection PyUnresolvedReferences
        if in_port is None or in_port.closed:
            in_port = open_in()
            logging.info(f"MIDI input {in_port}")
            converter = MidiConverter(in_port, out_port)
            converter.start()

        time.sleep(5)


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
    Thread(target=start_midi, args=(out_port,), daemon=True).start()
    time.sleep(5)

    in_port = open_midi_ports(ConfigName.pedal_commands, is_input=True)
    MidiController(s_ctrl, in_port).start()


if __name__ == "__main__":
    main()
