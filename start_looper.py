import os
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

from loop import ExtendedCtrl
from midi import MidiController
from screen import ScreenUpdater
from utils import open_midi_ports


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
    port_name = os.getenv("MIDI_PORT_NAME", "PedalCommands_out")
    in_port = open_midi_ports(port_name, True)
    if not in_port:
        raise RuntimeError(f"Failed to open MIDI port for commands input: {port_name}")

    r_upd, s_upd = Pipe(False)  # screen update messages
    r_ctrl, s_ctrl = Pipe(False)  # looper control messages

    p_upd = Process(target=process_updater, args=(r_upd,), daemon=True)
    p_ctrl = Process(target=process_control, args=(r_ctrl, s_upd), daemon=True)

    p_upd.start()
    p_ctrl.start()

    MidiController(s_ctrl, in_port).start()


if __name__ == "__main__":
    main()
