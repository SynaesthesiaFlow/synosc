from utils.midi_util import Instrument
import mido
import time
from queue import Queue


class AbletonMock:
    """
    mock to help build with dependency/parameter injection
    # TODO create midi events from mock synth on metronome timing to generate test inputs
    """
    qpm = 120.0

    def instrument_mock(self):
        instrument = Instrument()
        notes = [("C5", 100, 0, 0.5), ("E5", 100, 0, 0.5), ("G5", 100, 0, 0.5)]  # (note_name, velocity, start, end)
        instrument.create_midi(notes)


