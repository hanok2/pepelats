from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection

from loop import ExtendedCtrl
from midi import MidiController
from screen import ScreenUpdater


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

    def main():


        in_midi_port = open_midi_ports()


        r_upd, s_upd = Pipe(False)  # screen update messages
        r_ctrl, s_ctrl = Pipe(False)  # looper control messages

        p_upd = Process(target=proc_updater, args=(r_upd,), daemon=True)
        p_ctrl = Process(target=proc_ctrl, args=(r_ctrl, s_upd), daemon=True)

        p_upd.start()
        p_ctrl.start()

        MidiController(s_ctrl, in_midi_port).midi_control.start()


    main()
