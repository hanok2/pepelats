# noinspection PyUnusedLocal
import time

from utils import MainLoader


class MockedMixer:
    """Used to run on windows, there is no ALSA sound on windows"""

    def __init__(self):
        self.__vol_in: int = MainLoader.get("MIXER_IN", 30)
        self.__vol_out: int = MainLoader.get("MIXER_OUT", 100)

    def fade(self, seconds: int) -> None:
        time.sleep(seconds)

    def setvolume(self, vol: int, out: bool):
        if vol > 100 or vol < 0:
            return
        if out:
            self.__vol_out = vol
            MainLoader.set("MIXER_OUT", vol)
        else:
            self.__vol_in = vol
            MainLoader.set("MIXER_IN", vol)
        MainLoader.save()

    def getvolume(self, out: bool):
        if out:
            return self.__vol_out
        else:
            return self.__vol_in

    def change_volume(self, change_by: int, out: bool):
        self.setvolume(self.getvolume(out) + change_by, out)

    def mixer_info(self) -> str:
        return f"{self.__class__.__name__}"

    def __str__(self):
        return f"{self.__class__.__name__} out {self.getvolume(True)} in {self.getvolume(False)}"


if __name__ == "__main__":
    pass
