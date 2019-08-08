from utils.wrench import get_syn_config
from generators.models.melody_rnn import SynMelodyRNN

DEFAULT_QUARTERS_PER_MINUTE = 120.0
config = get_syn_config()

"""
TODO: magenta_midi integration:

def load_magenta_midi(self, syn_config):
    "magenta/interfaces/midi/magenta_midi.py"
    self.magenta_midi = self.load_magenta_midi(syn_config)
"""


class GenerativeMusicScene:
    """
    A digital scene for generating music
    """

    def __init__(self, syn_config):
        self.syn_config = syn_config
        self.melody_model = SynMelodyRNN()
        self.start_time = 0
        self.stop_signal = False
        self.signals = None
        self.channel = None
        self.qpm = self.syn_config['quarters_per_minute']

    def start_scene(self, qpm, start_time):
        """
        define generator interface to use here
        """

        # output_dir = "mag_out1"
        # primer_midi = "data/primer.mid"
        # SynMelodyRNN.midi_prior_generates_midi_melody(primer_midi, output_dir)
        # next_mid_out = "tmp-glob.midi"
        # midi_data = get_midi_aggr_dir(output_dir, next_mid_out)
        # gen_qpm_est = estimate_tempo(midi_data)
        # before = sme.get_qpm()
        # sme.update_metronome()
        # after = sme.get_qpm()
        # print(f"BEFORE metronome qpm: {before}")
        # print(f"AFTER metronome qpm: {after}")
        pass


def test():
    primer_midi = "/Users/davisdulin/src/synaesthesia/synosc/data/primer.mid"
    # primer_melody = f"{[60]}"
    output_dir = "/tmp/mag_tmp2.midi"
    SynMelodyRNN.midi_prior_generates_midi_melody(primer_midi, output_dir)


def main():
    test()


if __name__ == "__main__":
    main()

"""
generative model hacks:
1) generate lots of candidate samples for the next available time slot
2) create validator for selecting from generative model
    - vectorize the generation of samples with beam search
confidence interval for tempo estimate?

TODO
    - logging patterns from magenta
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
    - comb through magenta/music to better understand available util
    - magenta/protobuf/music.proto is probably a good reference for parameters to extract
    - idea:
        - get pipes setup for chords, drums, melody (magenta/pipelines)
        - give option to "fill in" missing sounds with magenta
    - turn file I/O into str handling
    - accrue midi context as sliding window w inertia
        - historical
        - recent
        - latest
    - stay on beat
        - filter if tempo validator fails?
    - continuously compliment what is being played with various musical pipelines
        - chords
        - drums
        - melody
    - get midi output from magenta as string
        - estimate the beat
    - align it for output
        - compare beat to metronome
        - warp
            - warp should be minimized by generating in rhythm with recent input
        - after processing, tie it to a future upcoming beat to start the playback
    - result = param to feed into ableton warp
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
- constraints to put on RNN to stay on beat?
    - i'm imagining some cyclical filter with a peak at the beat, and slope characteristic to that specific cycle
- performance comparison(?):
    1) run everything in a single interpreter with multiple threads
    2) have dedicated interpreters with an defined read/write interface

- Each SequenceExample will contain a sequence of inputs and a sequence of labels that represent a melody
        https://github.com/tensorflow/magenta/blob/master/magenta/pipelines/note_sequence_pipelines.py

Idea for new magenta midi interface protocol
    think i have an idea to make generative models more real-time for interaction. but i’m making it up, so plz call me on my bullshittin brainstorm:
    1) part of the reason models are slow is because they are batch: user gives the entire chunk of midi, and a chunk of midi comes out
    2) if it was instead a stream, it would be more real-time.
    3) to make it a stream, you could have a small midi unit input to the model, and get a small midi unit output
    4) but that would be shit because a lot of the context provided by a sequence is essential to compose musical structure
    5) if instead:
    - provide single unit of midi input to model, and output result
    - the next pass on the model provides the next midi unit input, appended to the end of all previous inputs, for sequential context
    - somehow constrain the model such that it adds on to what it already created in a way that maintains harmony, or something
    i’m not sure how you would impose the constraint of having the model result in the same output that it previously generated (after new notes have been added). but maybe you don’t have to, and could just have it be another input to the model, like the attention mechanisms from transformers.
    Not sure, green field, but this would mean the model could both (1) start outputting something right when someone starts to play, and (2) maintain and act on the existing musical context


    - MPE has continuous instead of midi?(discrete?)?
    - backprop continuous MPE for somekinda weird close neural net interactivity appreciation connection (audio/visual)
    - make smallest pythonic path of code between audio/visual interaction with neural net
   
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
