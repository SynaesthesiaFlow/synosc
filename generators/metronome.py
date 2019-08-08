import time
from magenta.interfaces.midi.midi_hub import Metronome
from utils.magenta_util import get_midi_hub_mock


class SynMetronome:
    """
    context manager for holding Magenta processes
    """

    def __init__(self, qpm, start_time, signals, channel):
        self.qpm = qpm
        self.start_time = start_time
        self.signals = signals
        self.channel = channel
        self.initialize_metronome_mock(qpm, self.start_time, signals=self.signals, channel=self.channel)

    def __enter__(self):
        self.start_time = time.time()
        self.midi_hub._metronome.start()

    def __exit__(self, *exc):
        print(f"*exc: {exc}")
        self.midi_hub.stop_metronome()

    def get_qpm(self):
        return self.midi_hub._metronome.qpm

    def initialize_metronome_mock(self, qpm, start_time, signals=None, channel=None):
        """
        Synchronized with Ableton for tempo alignment
        :param qpm:
        :param start_time:
        :param signals:
        :param channel:
        :return:
        """
        self.midi_hub = get_midi_hub_mock()
        if self.midi_hub._metronome is not None and self.midi_hub._metronome.is_alive():
            self.midi_hub._metronome.update(
                qpm, start_time, signals=signals, channel=channel)
        else:
            self.midi_hub._metronome = Metronome(
                self.midi_hub._outport, qpm, start_time, signals=signals, channel=channel)

    def start_metronome(self):
        self.midi_hub.start_metronome(start_time=self.start_time, qpm=self.qpm)

    def update_metronome(self, qpm):
        self.midi_hub._metronome.update(qpm=qpm, start_time=self.start_time)