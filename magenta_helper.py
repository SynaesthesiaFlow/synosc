"""
TODO
    - explore/find/brainstorm the basic features that we want, and get it plumbed all the way through
    - interface with core magenta tooling instead of outer shell scripts
    - create primer streaming input layer for magenta for more real-time interaction
        open questions:
            - does this even work? (see "decrease latency" below)
            - can it be fine tuned to work?
            - how to hold output from previous stream as constraint on current stream?
    - connect a Synth to a Magenta MIDI Interface (magenta/interfaces/midi/)
            AI-Jam reference: https://github.com/tensorflow/magenta-demos/tree/master/ai-jam-js
            - define a new Magenta MIDI Interface for real time interaction using streaming
    - comb through models for inspiration
    - comb through magenta/music to better understand available utils
    - magenta/protobuf/music.proto is probably a good reference for parameters to extract
    - idea:
        - get pipes setup for chords, drums, melody (magenta/pipelines)
        - give option to "fill in" missing sounds with magenta

- do we want to go for some kind of direct mapping between an instrument -> magenta -> LXEngine?
- which features do we want to expose from magenta?
        - call & response (melody_rnn, coconet, ...)
        - compliment/augment in real time
            - camouflage latency by requiring inertia behind rhythm/harmony?
        - it would be nice if there was a word-movers-distance equivalent to filling up frequency space with complimentary harmonies


- Magenta Parameters (collect here, and YAML what becomes wanted):
    /Users/davisdulin/src/synosc/magenta/magenta/music/constants.py
- midi_hub for notesequence conversion
- A MIDI clock to synchronize multiple `magenta_midi` instances. (midi_clock)
- midi_interaction: A module for implementing interaction between MIDI and SequenceGenerators.
        midi_interaction.CallAndResponseMidiInteraction()
-
"""
import subprocess
import pretty_midi
import mido
from mido import sockets
from mido.ports import MultiPort
import magenta
import ast
from util import get_syn_config
from contextlib import contextmanager
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.protobuf import generator_pb2
from magenta.protobuf import music_pb2
import tensorflow as tf


DEFAULT_QUARTERS_PER_MINUTE = 120.0

config = get_syn_config()
"""


@contextmanager
def managed_resource(*args, **kwds):
    # Code to acquire resource, e.g.:
    resource = acquire_resource(*args, **kwds)
    try:
        yield resource
    finally:
        # Code to release resource, e.g.:
        release_resource(resource)

>>> with managed_resource(timeout=3600) as resource:
...     # Resource is released at the end of this block,
...     # even if code in the block raises an exception
"""
from magenta.interfaces.midi.midi_hub import Metronome
class SynMagEther(object):
    """
    partial truth: stateless relations between Inbound and Outbound?
    context manager for holding Magenta processes
    Base class to be used for different context managers
        - Inbound, corresponds with OSC Server
        - Outbound, corresponds with OSC Client
        to correspond with the OSC client/server. really feels like its coming along! n we've got touch designers onboard :slightly_smiling_face:
    two types:
        - inbound
        - outbound

    """

    metronome = Metronome()

    def __init__(self):
        
        self.db1 = DB1()
        self.db2 = DB2()

    def __enter__(self):
        self.db1.__enter__()
        try:
            self.db2.__enter__()
        except:
            self.db1.__exit__(None, None, None) # I am not sure with None
            raise
        return self
    def __exit__(self, type, value, traceback):
        try:
            self.db1.__exit__(self, type, value, traceback)
        finally:
            self.db2.__exit__(self, type, value, traceback)


class SynMagEther:


    @contextmanager
    def manage_magenta_inbound(self, *args, **kwds):
        pass

    @contextmanager
    def manage_magenta_outbound(self, *args, **kwds):
        pass



    def manage_magenta_inbound(self, *args, **kwds):



    def manage_magenta_inbound(self, *args, **kwds):


class SynGenModels:

    @staticmethod
    def midi_prior_generates_midi_melody(primer_midi, output_dir):
        pass

    def get_midi_str(self, primer_midi):
        # primer_melody = magenta.music.Melody(ast.literal_eval(primer_mid))
        # primer_sequence = primer_melody.to_sequence(qpm=config['DEFAULT_QUARTERS_PER_MINUTE'])
        primer_sequence = magenta.music.midi_file_to_sequence_proto(primer_midi)
        if primer_sequence.tempos and primer_sequence.tempos[0].qpm:
            qpm = primer_sequence.tempos[0].qpm
        pass


    @staticmethod
    def midi_prior_generates_midi_melody(primer_midi):
        """
        decrease latency:
            - shorter datastream to melody RNN (e.g. no file io)
            - stream inputs: - start generating after receiving first midi packet of priming phrase
                              - continue appending to the priming phrase as it is played, while holding a constraint on the output to equal what was already previously generated (how is rhythm constrained? could this be done similarly?)
                              - start to play back generated melody after a defined pause time (which, with this method, in theory, could be sub 0 seconds, lending itself to complimentary real-time play)
                              - this way, the generative model starts figuring out what to say sooner, and starts playing it back sooner
                              - currently I/O is batch, but this is all stream and so should be handled as stream
        use melody_rnn with attention to generate a midi file from an input midi
        primer_midi: (path) to midi file
        primer_melody: (list) of pitches, replaces primer_midi
                       -2 = no event, -1 = note-off event, values 0 through 127 = note-on event for that MIDI pitch
        """
        config = "attention_rnn"
        bundle_path = "/Users/davisdulin/src/synaesthesia/synosc/data/attention_rnn.mag"
        cmd = f"./generate-rnn-midi.sh {config} {bundle_path} {output_dir} {primer_midi}"
        subprocess.run(cmd, shell=True)


class SynMidiUtil:
    """
    to be used closely with magenta/music/midi_io.py
    with additional utils
    more pretty_midi examples: https://github.com/craffel/pretty-midi/tree/master/examples
    """

    def serve_ports(self):
        out = MultiPort([mido.open_output(name) for name in ["SH-201" "SD-20 Part A"]])

        (host, port) = sockets.parse_address(":8080")
        with sockets.PortServer(host, port) as server:
            for message in server:
                print("Received {}".format(message))
                out.send(message)

    def _print_ports(self, heading, port_names):
        print(heading)
        for name in port_names:
            print("    '{}'".format(name))
        print()

    def print_ports(self):
        print()
        SynMidiUtil._print_ports("Input Ports:", mido.get_input_names())
        SynMidiUtil._print_ports("Output Ports:", mido.get_output_names())

    def get_midi(self, fname="example.mid"):
        midi_data = pretty_midi.PrettyMIDI(fname)
        return midi_data

    def create_midi(self):
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

    def estimate_tempo(self, midi_data):
        # Print an empirical estimate of its global tempo
        return midi_data.estimate_tempo()

    def get_musical_key(self, midi_data):
        # Compute the relative amount of each semitone across the entire song, a proxy for key
        total_velocity = sum(sum(midi_data.get_chroma()))
        return [sum(semitone) / total_velocity for semitone in midi_data.get_chroma()]

    def shift_instrument_notes(self, midi_data, n):
        # Shift all notes up by n semitones
        for instrument in midi_data.instruments:
            # Don't want to shift drum notes
            if not instrument.is_drum:
                for note in instrument.notes:
                    note.pitch += n

    def synthesize_midi(self, midi_data):
        # Synthesize the resulting MIDI data using sine waves
        audio_data = midi_data.synthesize()
        return audio_data


def test():
    primer_midi = "/Users/davisdulin/src/synaesthesia/synosc/data/primer.mid"
    # primer_melody = f"{[60]}"
    SynGenModels.midi_prior_generates_midi_melody(primer_midi)


def main():
    pass


if __name__ == "__main__":
    main()

"""
- Each SequenceExample will contain a sequence of inputs and a sequence of labels that represent a melody
        https://github.com/tensorflow/magenta/blob/master/magenta/pipelines/note_sequence_pipelines.py


convert to note sequences
        INPUT_DIRECTORY=/magenta/magenta/testdata/mid_only

        # TFRecord file that will contain NoteSequence protocol buffers.
        SEQUENCES_TFRECORD=/tmp/notesequence/test2.tfrecord

        convert_dir_to_note_sequences \
          --input_dir=$INPUT_DIRECTORY \
          --output_file=$SEQUENCES_TFRECORD \
          --recursive

Note Sequence Pipelines
    - https://github.com/tensorflow/magenta/blob/master/magenta/pipelines/note_sequence_pipelines.py
    - The bundle format 
        - a convenient way of combining the model checkpoint, metagraph, and some metadata about the model into a single file.
            https://github.com/tensorflow/magenta/blob/master/magenta/protobuf/generator.proto


convert NoteSequences into SequenceExamples
            Run the command below to extract melodies from our NoteSequences and save them as SequenceExamples
                    melody_rnn_create_dataset  --config='attention_rnn' --input=/tmp/notesequence/test2.tfrecord --output_dir=/tmp/melody_rnn/sequence_examples --eval_ratio=0.10


Train and Evaluate Model
        melody_rnn_train \
        --config=attention_rnn \
        --run_dir=/tmp/melody_rnn/logdir/run1 \
        --sequence_example_file=/tmp/melody_rnn/sequence_examples/training_melodies.tfrecord \
        --hparams="batch_size=64,rnn_layer_sizes=[64,64]" \
        --num_training_steps=20000

"""
