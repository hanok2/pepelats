import os
import time
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

import mido

from loop import ExtendedCtrl
from midi import MidiController
from screen import ScreenUpdater
from utils import ConfigName
from utils import open_midi_ports


def open_in():
    tmp = os.getenv(ConfigName.midi_port_names)
    return open_midi_ports(tmp, is_input=True)


def open_out():
    if not os.name == "posix":
        # on Windows need loopmidi application to create this port
        return open_midi_ports(ConfigName.pedal_commands, is_input=False)
    else:
        # on Linix create port form python
        # noinspection PyUnresolvedReferences
        return mido.open_output(ConfigName.pedal_commands, virtual=True)


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

    while True:
        in_port = open_midi_ports(ConfigName.pedal_commands, is_input=True)
        if not in_port:
            time.sleep(2)
        else:
            break

    MidiController(s_ctrl, in_port).start()


if __name__ == "__main__":
    main()
