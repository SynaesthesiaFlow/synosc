import pretty_midi
import mido
from mido import sockets
from mido.ports import MultiPort
import os
import time
from queue import Queue
"""
pretty_midi examples: https://github.com/craffel/pretty-midi/tree/master/examples
"""


class MockMidiPort(mido.ports.BaseIOPort):

    def __init__(self):
        super(MockMidiPort, self).__init__()
        self.message_queue = Queue()

    def send(self, msg):
        msg.time = time.time()
        self.message_queue.put(msg)


def get_midi_port_mock():
    return MockMidiPort()


def qpm_to_bpm(qpm, numerator=4, denominator=4):
    """
    The bottom number of the time signature indicates a certain kind of note
    and the top note reveals how many of those notes there are in each measure
     quarter_note_tempo : (float) Quarter note tempo.
     numerator : (int) Numerator of time signature.
     denominator : (int) Denominator of time signature.
     Returns: bpm: (float) Tempo in beats per minute.
     """
    return pretty_midi.qpm_to_bpm(qpm, numerator, denominator)


def bpm_to_qpm():
    pass


def get_abs_fnames_in_dir(directory_name):
    return [os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", directory_name, f) for f in os.listdir(directory_name)]


def get_midi_aggr_dir(in_dir, out_f):
    midi_files = get_abs_fnames_in_dir(in_dir)
    ml = list()
    for midif in midi_files:
        with open(midif, "rb") as f:
            m = f.read()
        ml.append(m)
    b = "\n".encode().join(ml)
    print("B: " + str(b))
    with open(out_f, "wb") as f:
        f.write(b)
    return ml


def serve_ports():
    out = MultiPort([mido.open_output(name) for name in ["SH-201" "SD-20 Part A"]])

    (host, port) = sockets.parse_address(":8080")
    with sockets.PortServer(host, port) as server:
        for message in server:
            print("Received {}".format(message))
            out.send(message)


def _print_ports(heading, port_names):
    print(heading)
    for name in port_names:
        print("    '{}'".format(name))
    print()


def print_ports():
    print()
    _print_ports("Input Ports:", mido.get_input_names())
    _print_ports("Output Ports:", mido.get_output_names())


def get_midi(fname="example.mid"):
    midi_data = pretty_midi.PrettyMIDI(fname)
    return midi_data


class Instrument:
    def __init__(self, instrument_name="Cello"):
        self.midi = pretty_midi.PrettyMIDI()
        instrument_program = pretty_midi.instrument_name_to_program(instrument_name)
        self.instrument = pretty_midi.Instrument(program=instrument_program)

    def create_midi(self, notes):
        for note_name, velocity, start, end in notes:
            # Retrieve the MIDI note number for this note name
            note_number = pretty_midi.note_name_to_number(note_name)
            # Create a Note instance, starting at 0s and ending at .5s
            note = pretty_midi.Note(velocity=velocity, pitch=note_number, start=start, end=end)
            # Add it to our cello instrument
            self.instrument.notes.append(note)
        # Add the cello instrument to the PrettyMIDI object
        self.midi.instruments.append(self.instrument)
        # Write out the MIDI data
        self.midi.write("cello-C-chord.mid")


def create_midi():
    cello_c_chord = pretty_midi.PrettyMIDI()
    cello_program = pretty_midi.instrument_name_to_program("Cello")
    cello = pretty_midi.Instrument(program=cello_program)
    # Iterate over note names, which will be converted to note number later
    for note_name in ["C5", "E5", "G5"]:
        # Retrieve the MIDI note number for this note name
        note_number = pretty_midi.note_name_to_number(note_name)
        # Create a Note instance, starting at 0s and ending at .5s
        note = pretty_midi.Note(velocity=100, pitch=note_number, start=0, end=0.5)
        # Add it to our cello instrument
        cello.notes.append(note)
    # Add the cello instrument to the PrettyMIDI object
    cello_c_chord.instruments.append(cello)
    # Write out the MIDI data
    cello_c_chord.write("cello-C-chord.mid")


def estimate_tempo(midi_data):
    # Print an empirical estimate of its global tempo
    return midi_data.estimate_tempo()


def get_musical_key(midi_data):
    # Compute the relative amount of each semitone across the entire song, a proxy for key
    total_velocity = sum(sum(midi_data.get_chroma()))
    return [sum(semitone) / total_velocity for semitone in midi_data.get_chroma()]


def shift_instrument_notes(midi_data, n):
    # Shift all notes up by n semitones
    for instrument in midi_data.instruments:
        # Don't want to shift drum notes
        if not instrument.is_drum:
            for note in instrument.notes:
                note.pitch += n


def synthesize_midi(midi_data):
    # Synthesize the resulting MIDI data using sine waves
    audio_data = midi_data.synthesize()
    return audio_data
