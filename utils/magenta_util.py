from utils.midi_util import get_midi_port_mock
from magenta.interfaces.midi.midi_hub import TextureType, MidiHub


def get_midi_hub_mock():
    port = get_midi_port_mock()
    midi_hub = MidiHub([port], [port], TextureType.POLYPHONIC)
    return midi_hub
