from utils import IS_LINUX

if IS_LINUX:
    from mixer._alsamixer import AlsaMixer as Mixer
else:
    from mixer._mockedmixer import MockedMixer as Mixer
