import logging
import os
import sys
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from threading import Thread

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
    if not os.name == "posix":
        # on Windows need loopmidi application to create this port
        return open_midi_ports(ConfigName.pedal_commands, is_input=False)
    else:
        # on Linix create port form python
        # noinspection PyUnresolvedReferences
        tmp = mido.open_output(ConfigName.pedal_commands, virtual=True)
        logging.info(f"Opened virtual port: {tmp}")
        return tmp


def thread_converter():
    in_port = open_in()
    if not in_port:
        logging.error(f"MIDI in conection failed")
        sys.exit(1)

    out_port = open_out()
    if not out_port:
        logging.error(f"MIDI out conection failed")
        sys.exit(1)

    converter = MidiConverter(in_port, out_port)
    converter.start()


def process_control(r_conn: Connection, s_conn: Connection):
    pepelats = ExtendedCtrl(s_conn)
    pepelats.start()
    while True:
        msg = r_conn.recv()
        pepelats.process_message(msg)


def process_updater(r_conn: Connection):
    screen_updater = ScreenUpdater()
    screen_updater.start()
    while True:
        msg = r_conn.recv()
        screen_updater.process_message(msg)


def main():
    r_upd, s_upd = Pipe(False)  # screen update messages
    r_ctrl, s_ctrl = Pipe(False)  # looper control messages

    p_upd = Process(target=process_updater, args=(r_upd,), daemon=True)
    p_ctrl = Process(target=process_control, args=(r_ctrl, s_upd), daemon=True)

    p_upd.start()
    p_ctrl.start()

    t_conv = Thread(target=thread_converter, daemon=True)
    t_conv.start()

    in_port = open_midi_ports(ConfigName.pedal_commands, is_input=True)
    if not in_port:
        logging.error(f"Failed to open port: {ConfigName.pedal_commands}")
        sys.exit(1)
    MidiController(s_ctrl, in_port).start()


if __name__ == "__main__":
    main()
