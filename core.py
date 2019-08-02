import subprocess


def midi_prior_generates_midi_melody(primer_midi):
    """
    uses melody_rnn with attention to generate a midi file from an input midi
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
    primer_midi = f"/Users/davisdulin/src/synaesthesia/synosc/data/primer.mid"
    # primer_melody = f"{[60]}"
    midi_prior_generates_midi_melody(primer_midi)


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










