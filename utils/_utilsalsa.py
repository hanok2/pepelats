import os
from typing import Tuple, Union

import numpy as np
import sounddevice as sd


def set_alsa_default_device() -> None:
    """Look for USB Audio device and set it default"""
    sd_in = os.getenv("SD_IN", "USB Audio")
    sd_out = os.getenv("SD_OUT", "USB Audio")
    sd_in_out = sd.default.device
    in_found = out_found = False
    for k, dev in enumerate(sd.query_devices()):
        if not in_found and sd_in in dev["name"]:
            sd_in_out[0] = k
        if not out_found and sd_out in dev["name"]:
            sd_in_out[1] = k

    sd.default.device = sd_in_out


def get_max_channels() -> Tuple[int, int]:
    in_d = sd.default.device[0]
    out_d = sd.default.device[1]
    assert type(in_d) == int
    assert type(out_d) == int
    in_d = sd.query_devices(in_d)
    out_d = sd.query_devices(out_d)
    assert type(in_d) == dict
    assert type(out_d) == dict
    assert "max_input_channels" in in_d
    assert "max_output_channels" in out_d
    in_d = in_d["max_input_channels"]
    out_d = out_d["max_output_channels"]
    assert type(in_d) == int
    assert type(out_d) == int
    return in_d, out_d


set_alsa_default_device()
IN_CHANNELS, OUT_CHANNELS = get_max_channels()
if OUT_CHANNELS != 2:
    raise RuntimeError(f"ALSA audio device must have 2 output channels, got {OUT_CHANNELS}")
if IN_CHANNELS not in [1, 2]:
    raise RuntimeError(f"ALSA audio device must have 1 or 2 input channels, got {IN_CHANNELS}")


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
    if IN_CHANNELS == 1:
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


SD_RATE: int = int(os.getenv("SD_RATE", "48000"))
sd.default.samplerate = SD_RATE
sd.default.channels = IN_CHANNELS, OUT_CHANNELS
SD_TYPE: str = 'int16'
sd.default.dtype = [SD_TYPE, SD_TYPE]
sd.default.latency = ('low', 'low')
MAX_LEN: int = int(os.getenv("MAX_LEN_SECONDS", "60")) * SD_RATE
MAX_32_INT = 2 ** 32 - 1
SD_MAX: int = np.iinfo(SD_TYPE).max


def make_zero_buffer(buff_len: int) -> np.ndarray:
    if buff_len < 0 or buff_len > MAX_LEN:
        raise ValueError(f"make_zero_buffer() incorrect parameter: {buff_len}")
    return np.zeros((buff_len, OUT_CHANNELS), SD_TYPE)


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
    def main():
        set_alsa_default_device()

        result1 = sd.query_devices()

        print("=========================")
        print(result1)
        print("=========================")

        result1 = sd.query_devices(sd.default.device)

        print("=========================")
        print(result1)
        print("=========================")


    main()
