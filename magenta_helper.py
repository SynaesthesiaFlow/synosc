import subprocess
import pretty_midi


class ProtocolConverter:
    """
    convert to/from OSC/MIDI
    learning curve:
        - osc is tied to a network and URL encoding which is an intimidating transport layer
    """
    def midi_to_osc():

        pass

    def osc_to_midi():
        pass

    


class SynMidiUtil:
    """
    to be used closely with magenta/music/midi_io.py
    with additional utils
    more pretty_midi examples: https://github.com/craffel/pretty-midi/tree/master/examples
    """

    def get_midi():
        midi_data = pretty_midi.PrettyMIDI('example.mid')
        return midi_data

    def create_midi():
        cello_c_chord = pretty_midi.PrettyMIDI()
        cello_program = pretty_midi.instrument_name_to_program('Cello')
        cello = pretty_midi.Instrument(program=cello_program)
        # Iterate over note names, which will be converted to note number later
        for note_name in ['C5', 'E5', 'G5']:
            # Retrieve the MIDI note number for this note name
            note_number = pretty_midi.note_name_to_number(note_name)
            # Create a Note instance, starting at 0s and ending at .5s
            note = pretty_midi.Note(
                velocity=100, pitch=note_number, start=0, end=.5)
            # Add it to our cello instrument
            cello.notes.append(note)
        # Add the cello instrument to the PrettyMIDI object
        cello_c_chord.instruments.append(cello)
        # Write out the MIDI data
        cello_c_chord.write('cello-C-chord.mid')

    def estimate_tempo(midi_data):
        # Print an empirical estimate of its global tempo
        return midi_data.estimate_tempo()

    def get_musical_key(midi_data):
        # Compute the relative amount of each semitone across the entire song, a proxy for key
        total_velocity = sum(sum(midi_data.get_chroma()))
        return [sum(semitone)/total_velocity for semitone in midi_data.get_chroma()]

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


class SynGenModels:

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
        
        
        # subprocess.call(["./generate-rnn-midi.sh", config, bundle_path, output_dir], shell=True)
        cmd = f"./generate-rnn-midi.sh {config} {bundle_path} {output_dir} {primer_midi}"
        subprocess.run(cmd, shell=True)


def test():
    primer_midi = "/Users/davisdulin/src/synaesthesia/synosc/data/primer.mid"
    # primer_melody = f"{[60]}"
    SynGenModels.midi_prior_generates_midi_melody(primer_midi)


def main():
    test()


if __name__ == "__main__":
    main()
"""
Melody RNN: a first pass
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










