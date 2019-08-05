"""
TODO
    - interface with core magenta tooling instead of outer shell scripts

- do we want to go for some kind of direct mapping between an instrument -> magenta -> LXEngine?
- which features do we want to expose from magenta?
        - call & response (melody_rnn, coconet, ...)
        - compliment/augment in real time
            - camouflage latency by requiring inertia behind rhythm/harmony?
        - it would be nice if there was a word-movers-distance equivalent to filling up frequency space with complimentary harmonies

MIR Goals:
    - Estimate Consonance and Dissonance
        - https://music.stackexchange.com/questions/4439/is-there-a-way-to-measure-the-consonance-or-dissonance-of-a-chord
        - http://musicalgorithms.ewu.edu/learnmore/MoreRoughness.html
        - The term roughness describes an aural sensation and was introduced in the acoustics and psychoacoustics literature by Helmholtz (end of the nineteenth century) to label harsh, raspy, hoarse sounds. Within the Western musical tradition, auditory roughness constitutes one of the perceptual correlates of the multidimensional concept of dissonance.
        - (a)   If the fluctuation rate is smaller than the critical bandwidth, then a single tone is perceived either with fluctuating loudness (beating) or with roughness.
          (b) If the fluctuation rate is larger than the critical bandwidth, then a complex tone is perceived, to which one or more pitches can be assigned but which, in general, exhibits no beating or roughness.
    - beat estimation


some noteworthy packages from magenta
    dopamine-rl, gym: A framework for flexible Reinforcement Learning research
    librosa: LibROSA is a python package for music and audio analysis
    mir_eval: Music Information Retrieval system
    audioread: Decode audio files using whichever backend is available
    greenlet: lightweight concurrency https://stackoverflow.com/questions/15556718/greenlet-vs-threads
    bokeh: viz tool
    resampy: Efficient sample rate conversion in python
    absl-py: Google's own Python code base,
    mido: midi util

"""
import subprocess
import pretty_midi
import mido
from mido import sockets
from mido.ports import MultiPort


class SynGenModels:

    @staticmethod
    def midi_prior_generates_midi_melody(primer_midi):
        """
        use melody_rnn with attention to generate a midi file from an input midi
        primer_midi: (path) to midi file
        primer_melody: (list) of pitches, replaces primer_midi
                       -2 = no event, -1 = note-off event, values 0 through 127 = note-on event for that MIDI pitch
        """
        config = "attention_rnn"
        bundle_path = "/Users/davisdulin/src/synaesthesia/synosc/data/attention_rnn.mag"
        output_dir = "/tmp/melody_rnn/generated"
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
