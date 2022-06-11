import logging
import os
import sys
from datetime import datetime
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

from loop import ExtendedCtrl
from midi import MidiController, MidiConverter
from screen import ScreenUpdater
from utils import ConfigName, open_midi_ports


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


if __name__ == "__main__":
    #  freeze_support()
    logging.getLogger().addHandler(logging.StreamHandler())
    dtm = datetime.now()
    logging.getLogger().setLevel(logging.INFO)
    logging.info(f"Starting Pepelats looper: {dtm}")

    if ConfigName.use_typing in sys.argv or not os.name == "posix":
        from midi import KbdMidiPort

        in_midi_port = KbdMidiPort()
    else:
        in_midi_port = open_midi_ports()

    if in_midi_port is None:
        logging.error("Failed to connecting to MIDI input ports")
        sys.exit(1)
    else:
        logging.info(f"Connected to MIDI input port {in_midi_port.name}")

    r_upd, s_upd = Pipe(False)  # screen update messages
    r_ctrl, s_ctrl = Pipe(False)  # looper control messages

    p_upd = Process(target=proc_updater, args=(r_upd,), daemon=True)
    p_ctrl = Process(target=proc_ctrl, args=(r_ctrl, s_upd), daemon=True)

    p_upd.start()
    p_ctrl.start()

    if ConfigName.ext_conv in in_midi_port.name:
        midi_control = MidiController(s_ctrl, in_midi_port)
    else:
        midi_control = MidiConverter(s_ctrl, in_midi_port)

    midi_control.start()

    print("=========Done==============")
