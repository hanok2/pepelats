import json
import logging
import os
from typing import Tuple, Union, List

import mido
import numpy as np
import sounddevice as sd

from utils._utilsother import ConfigName


def list_from_str(s: str) -> List[str]:
    # noinspection PyBroadException
    try:
        new_s = s.strip(' ,').replace("'", "").replace('"', '').replace(',', '","')
        return json.loads(f'["{new_s}"]')
    except Exception as _:
        pass


def open_midi_ports(port_names_str: str, is_input: bool):
    port_names: List[str] = list_from_str(port_names_str)
    if not port_names:
        raise RuntimeError(f"List of MIDI port names is empty: {port_names_str}")

    # noinspection PyUnresolvedReferences
    port_list = mido.get_input_names() if is_input else mido.get_output_names()
    for name in port_names:
        for port_name in port_list:
            if name in port_name:
                print(f"opening: {port_name} input: {is_input}")
                if is_input:
                    # noinspection PyUnresolvedReferences
                    return mido.open_input(port_name)
                else:
                    # noinspection PyUnresolvedReferences
                    return mido.open_output(port_name)


def find_usb() -> None:
    """Look for USB Audio device and set it default"""
    usb_audio_str: str = os.getenv(ConfigName.usb_audio_names)
    usb_audio = list_from_str(usb_audio_str)
    if not usb_audio:
        logging.error(f"Failed to parse usb audio names string: {usb_audio_str}")
        return

    all_devices = sd.query_devices()
    for k, dev in enumerate(all_devices):
        for sd_name in usb_audio:
            full_name = dev["name"]
            if sd_name in full_name:
                logging.info(f"Found requested device {sd_name} in {full_name}")
                sd.default.device = k, k
                return


find_usb()
IN_CH = sd.query_devices(sd.default.device[0])["max_input_channels"]
OUT_CH = sd.query_devices(sd.default.device[1])["max_output_channels"]
if OUT_CH != 2:
    raise RuntimeError(f"ALSA audio device must have 2 output channels, got {OUT_CH}")
if IN_CH not in [1, 2]:
    raise RuntimeError(f"ALSA audio device must have 1 or 2 input channels, got {IN_CH}")


def calc_slices(buff_len: int, data_len: int, idx: int) -> Tuple[slice, Union[slice, None]]:
    assert 0 < data_len <= buff_len, f"Must be: 0 < data_len {data_len} <= buff_len {buff_len}"
    idx1 = idx % buff_len
    idx2 = (idx + data_len) % buff_len
    if idx2 > idx1:
        return slice(idx1, idx2), None
    else:
        return slice(idx1, buff_len), slice(0, idx2)


def record_sound_buff(buff: np.ndarray, np_data: np.ndarray, idx: int) -> None:
    assert buff.ndim == np_data.ndim
    data_len = len(np_data)
    if IN_CH == 1:
        np_data = np.broadcast_to(np_data, (data_len, 2))
    slice1, slice2 = calc_slices(len(buff), data_len, idx)
    if slice2 is None:
        buff[slice1] += np_data[:]
    else:
        s1 = slice1.stop - slice1.start
        s2 = slice2.stop - slice2.start
        buff[slice1] += np_data[0:s1]
        buff[slice2] += np_data[s1:s1 + s2]


def play_sound_buff(buff: np.ndarray, np_data: np.ndarray, idx: int) -> None:
    assert buff.ndim == np_data.ndim
    data_len = len(np_data)
    slice1, slice2 = calc_slices(len(buff), data_len, idx)
    if slice2 is None:
        np_data[:] += buff[slice1]
    else:
        s1 = slice1.stop - slice1.start
        np_data[:s1] += buff[slice1]
        np_data[s1:] += buff[slice2]


SD_RATE: int = int(os.getenv("SD_RATE", "44100"))
sd.default.samplerate = SD_RATE
SD_TYPE: str = 'int16'
sd.default.dtype = [SD_TYPE, SD_TYPE]
sd.default.latency = ('low', 'low')
MAX_LEN: int = int(os.getenv("MAX_LEN_SECONDS", "60")) * SD_RATE
MAX_32_INT = 2 ** 32 - 1
SD_MAX: int = np.iinfo(SD_TYPE).max


def make_zero_buffer(buff_len: int) -> np.ndarray:
    if buff_len < 0 or buff_len > MAX_LEN:
        raise ValueError(f"make_zero_buffer() incorrect parameter: {buff_len}")
    return np.zeros((buff_len, 2), SD_TYPE)


def sound_test(buffer: np.ndarray, duration_sec: float, record: bool) -> None:
    if not (buffer.ndim == 2 and buffer.shape[1] == 2):
        raise RuntimeError("Buffer for playback must have 2 channels")
    idx = 0

    # noinspection PyUnusedLocal
    def callback(in_data, out_data, frame_count, time_info, status):
        nonlocal idx

        out_data[:] = 0
        assert len(out_data) == len(in_data) == frame_count
        play_sound_buff(buffer, out_data, idx)
        if record:
            record_sound_buff(buffer, in_data, idx)
        idx += frame_count

    with sd.Stream(callback=callback, dtype=buffer.dtype):
        sd.sleep(int(duration_sec * 1000))


def make_sin_sound(sound_freq: int, duration_sec: float, amplitude: int = 3000) -> np.ndarray:
    points_in_array = int(sd.default.samplerate * duration_sec)
    t = np.linspace(0, duration_sec, points_in_array)
    x = amplitude * np.sin(2 * np.pi * sound_freq * t)
    x = x.astype("int16")[:, np.newaxis]
    x = np.column_stack((x, x))
    return x


def make_changing_sound() -> np.ndarray:
    a = make_sin_sound(330, 0.3)
    b = make_sin_sound(550, 0.3)
    return np.concatenate((a, b, a), axis=0)


if __name__ == "__main__":
    def run():
        print("=========================")
        print(sd.query_devices())
        print("=========================")

        print("=========================")
        print(sd.query_devices(sd.default.device[0]))
        print(sd.query_devices(sd.default.device[1]))
        print("=========================")


    run()
