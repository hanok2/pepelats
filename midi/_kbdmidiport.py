from queue import Queue
from typing import Dict

import keyboard
import mido


class KbdMidiPort:
    """Using keyboard keys instead of MIDI notes"""

    def __init__(self, kbd_notes: Dict[str, int]):
        self.name: str = "Typing keyboard as MIDI port"
        self.__kbd_notes = kbd_notes
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
        test_port = KbdMidiPort({"1": 60, "2": 62, "3": 64, "4": 65, "q": 12, "w": 13})

        while True:
            test_msg = test_port.receive()
            print(test_msg)


    test_1()
