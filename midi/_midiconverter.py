from multiprocessing.connection import Connection
from threading import Timer
from typing import Dict

import mido

from midi._midicontroller import MidiController
from utils import always_true, ConfigName, JsonDictLoader


def is_midi_ctrl_chg(msg):
    """ if MIDI message is Ctrl_chg """
    if msg is None:
        return False
    byte0 = msg.bytes()[0]
    return 0xb0 <= byte0 <= 0xbf


def is_midi_note_on(msg):
    byte0 = msg.bytes()[0]
    return 0x90 <= byte0 <= 0x9f


def is_midi_note_off(msg):
    byte0 = msg.bytes()[0]
    return 0x80 <= byte0 <= 0x8f


def is_midi_note(msg):
    byte0 = msg.bytes()[0]
    return 0x80 <= byte0 <= 0x9f


class MidiCcToNote:
    """Convert MIDI control change to note ON/OFF messages.
    Needed for expression pedal to send note ON/OF when pedal goes Down/Up
    Use this to convert expression pedal CC into note ON/OFF"""

    def __init__(self):
        self.prev_msg = mido.Message.from_bytes([0x80, 0, 0])
        self.sent_on = False

    def convert(self, msg):
        if is_midi_note(msg):
            self.prev_msg = msg
            self.sent_on = False
            return msg

        if not (is_midi_ctrl_chg(msg) and is_midi_ctrl_chg(self.prev_msg)):
            self.prev_msg = msg
            self.sent_on = False
            return None

        if msg.bytes()[1] != self.prev_msg.bytes()[1]:
            self.prev_msg = msg
            self.sent_on = False
            return None

        # expression pedal goes down, hence value goes down
        if self.prev_msg.bytes()[2] > msg.bytes()[2]:
            if not self.sent_on:
                self.prev_msg = msg
                self.sent_on = True
                return mido.Message.from_bytes([0x90, msg.bytes()[1], 100])
            else:
                return None
        else:
            if self.sent_on:
                self.prev_msg = msg
                self.sent_on = False
                return mido.Message.from_bytes([0x80, msg.bytes()[1], 0])
            else:
                return None


class MidiConverter(MidiController):
    """Count MIDI notes to increase number of messages MIDI pedal send,
    tap, double tap, long tap - send different notes. Count algorithm:
    --take the original note 60, find the mapped note 80
        --to mapped note add number of counted taps e.g. 80+2
        --add 5 if the last tap is long e.g. 80+2+5, send note 87
        --after inactivity period ~0.6 sec. count of taps set to zero"""

    count_restart_seconds = 0.600

    def __init__(self, s_conn: Connection, in_port):
        super().__init__(s_conn, in_port)
        self.__mapped_notes: Dict[str, int] = \
            JsonDictLoader("etc/count/mapped_notes.json").get(ConfigName.mapped_notes, None)

        self.__on_count: int = 0
        self.__off_count: int = 0
        self.__past_count_note: int = 0  # mapped for count
        self.__past_note: int = -1  # original MIDI note
        self.__midi_cc_to_note = MidiCcToNote()

    def start(self) -> None:
        assert always_true("Started MIDI note counter")
        while True:
            msg = self._in_port.receive()
            msg = self.__midi_cc_to_note.convert(msg)
            if msg is None:
                continue
            note = msg.bytes()[1]
            if str(note) not in self.__mapped_notes:
                continue

            is_on = is_midi_note_on(msg)
            if is_on and self.__past_note != note:
                # do not sent same note many times, we count it below
                self._translator.translate_and_send(str(note))

            self.__past_note = note
            count_note: int = self.__mapped_notes.get(str(note), None)
            if count_note:
                self.__update_count(count_note, is_on)
                on_count, off_count = self.__on_count, self.__off_count
                Timer(MidiConverter.count_restart_seconds, self.__count_and_send,
                      [on_count, off_count, count_note]).start()

    def __update_count(self, count_note: int, is_on: bool) -> None:
        # if we got another note number, restart count
        if self.__past_count_note != count_note:
            self.__on_count = self.__off_count = 0
            self.__past_count_note = count_note

        if is_on:
            self.__on_count += 1
        else:
            # old OFF note may come before ON, we correct
            if self.__on_count > 0:
                self.__off_count += 1

    def __count_and_send(self, on_count: int, off_count: int, count_note: int) -> None:
        # if we came here after a delay and note counts have changed we do not send
        self.__past_note = -1
        if self.__past_count_note != count_note \
                or self.__on_count != on_count \
                or self.__off_count != off_count:
            return

        # note and count did not change for long, we send MIDI
        count_note += self.__on_count
        if self.__on_count > self.__off_count:
            count_note += 5

        self.__on_count = self.__off_count = 0

        self._translator.translate_and_send(str(count_note))

    def __str__(self):
        return f"{self.__class__.__name__} note={self.__past_count_note} " \
               f"on_count={self.__on_count} off_count={self.__off_count}"


if __name__ == "__main__":
    pass
