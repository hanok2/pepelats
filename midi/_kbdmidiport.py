import logging
import os
import sys
from json import loads
from queue import Queue
from typing import Dict

import keyboard
import mido

from utils import ConfigName


class KbdMidiPort:
    """Using keyboard keys instead of MIDI notes"""

    def __init__(self):
        self.name: str = "Typing keyboard"
        kbd_map_str: str = os.getenv(ConfigName.kbd_notes)
        self.__kbd_notes: Dict[str, int] = dict()
        if kbd_map_str:
            try:
                self.__kbd_notes: Dict = loads("{" + kbd_map_str + "}")
            except Exception as ex:
                logging.error(f"Failed to parse {ConfigName.kbd_notes} error: {ex}\nstring value: {kbd_map_str}")
                sys.exit(1)

        self.__queue = Queue()
        self.pressed_key = False
        keyboard.on_press(callback=self.on_press, suppress=True)
        keyboard.on_release(callback=self.on_release, suppress=True)

    def on_press(self, kbd_event):
        # print(type(kbd_event), str(kbd_event.__dict__))
        if kbd_event.name == "esc":
            keyboard.unhook_all()
            print("Done unhook_all !!!")
            return

        val = self.__kbd_notes.get(kbd_event.name, None)
        if val is not None and not self.pressed_key:
            msg = mido.Message.from_bytes([0x90, val, 100])
            self.__queue.put(msg)
            self.pressed_key = True

    def on_release(self, kbd_event):
        val = self.__kbd_notes.get(kbd_event.name, None)
        if val is not None and self.pressed_key:
            msg = mido.Message.from_bytes([0x80, val, 0])
            self.__queue.put(msg)
            self.pressed_key = False

    def receive(self, block: bool = True):
        return self.__queue.get(block)


if __name__ == "__main__":
    def test_1():
        test_port = KbdMidiPort()

        while True:
            test_msg = test_port.receive()
            print(test_msg)


    test_1()
