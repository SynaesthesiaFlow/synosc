import pretty_midi
import mido
from mido import sockets
from mido.ports import MultiPort

"""
to be used closely with magenta/music/midi_io.py
with additional utils
more pretty_midi examples: https://github.com/craffel/pretty-midi/tree/master/examples
"""

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

def qpm_to_bpm(quarter_note_tempo, numerator, denominator):
    """
    quarter_note_tempo : float

    Quarter note tempo.

    numerator : int

    Numerator of time signature.

    denominator : int

    Denominator of time signature.

    Returns:
    bpm : float

    Tempo in beats per minute.
    :return:
    """
    return pretty_midi.pretty_midi.qpm_to_bpm(quarter_note_tempo, numerator, denominator)


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