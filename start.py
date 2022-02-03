import sys
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from threading import Thread

from loop import ExtendedCtrl
from midi import MidiController, MidiConverter, ScreenUpdater
from utils import ConfigName, get_midi_port


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
    in_midi_port = get_midi_port()
    if in_midi_port is None:
        print("Failed to connecting to MIDI input ports")
        sys.exit(1)

    r_upd, s_upd = Pipe(False)  # screen update messages
    r_ctrl, s_ctrl = Pipe(False)  # looper control messages

    if ConfigName.one_process in sys.argv:
        """one process version"""
        p_upd = Thread(target=proc_updater, args=(r_upd,), daemon=True)
        p_ctrl = Thread(target=proc_ctrl, args=(r_ctrl, s_upd), daemon=True)
    else:
        """multi process version"""
        p_upd = Process(target=proc_updater, args=(r_upd,), daemon=True)
        p_ctrl = Process(target=proc_ctrl, args=(r_ctrl, s_upd), daemon=True)

    p_upd.start()
    p_ctrl.start()

    if ConfigName.no_converter in sys.argv:
        """use external MIDI note counter converter module"""
        midi_contr = MidiController(s_ctrl, in_midi_port)
    else:
        midi_contr = MidiConverter(s_ctrl, in_midi_port)

    midi_contr.start()

    print("=========Done==============")
