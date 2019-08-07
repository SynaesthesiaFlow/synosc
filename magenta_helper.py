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
    - turn file I/O into str handling
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
"""
import subprocess
import pretty_midi
import mido

from mido import sockets
from mido.ports import MultiPort
import magenta
import ast
from contextlib import contextmanager
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.protobuf import generator_pb2
from magenta.protobuf import music_pb2
import tensorflow as tf

import time
from queue import Queue


from magenta.interfaces.midi.midi_hub import Metronome
from magenta.interfaces.midi import midi_hub
from util.util import get_syn_config
from magenta.common import concurrency
from util.midi_util import estimate_tempo
# from util.midi_util import get_midi_aggr_dir

DEFAULT_QUARTERS_PER_MINUTE = 120.0

config = get_syn_config()

from magenta.interfaces.midi.midi_hub import Metronome

mag_config = get_syn_config()["magenta"]


class MockMidiPort(mido.ports.BaseIOPort):

  def __init__(self):
    super(MockMidiPort, self).__init__()
    self.message_queue = Queue()

  def send(self, msg):
    msg.time = time.time()
    self.message_queue.put(msg)


class AbletonMock:
    """
    mock to help build with dependency/parameter injection
    """
    qpm = 120.0


class SynMagEther(object):
    """
    context manager for holding Magenta processes
    dependency injection is key
    two types:
        - inbound
        - outbound
    Ableton:
        - opens MIDI ports
    """

    def __init__(self, qpm, start_time, signals=None, channel=None):
        # self.start_metronome()
        self.port = MockMidiPort()
        self.midi_hub = midi_hub.MidiHub([self.port], [self.port], midi_hub.TextureType.POLYPHONIC)
        if self.midi_hub._metronome is not None and self.midi_hub._metronome.is_alive():
            self.midi_hub._metronome.update(
                qpm, start_time, signals=signals, channel=channel)
        else:
            self.midi_hub._metronome = Metronome(
                self.midi_hub._outport, qpm, start_time, signals=signals, channel=channel)

    def __enter__(self):
        self.start_time = time.time()
        self.midi_hub._metronome.start()

    def __exit__(self, *exc):
        print(f"*exc: {exc}")
        self.midi_hub.stop_metronome()

    def start_metronome(self):
        """
        - metronome with mocked port, to be synced with Ableton
        - fine tune outgoing generated music s.t. it aligns with tempo

        TODO
            - get midi output from magenta as string
                - estimate the beat
            - align it for output
                - compare beat to metronome
                - warp
                - after processing, tie it to a future upcoming beat to start the playback
            - result = param to feed into ableton warp
            - dynamic metronome without re-initializing: change metronome qpm on-the-fly
        """
        self.midi_hub.start_metronome(start_time=self.start_time, qpm=mag_config["default_quarters_per_minute"])


def test_cm():
    qpm = 120.0
    start_time = time.time()
    with SynMagEther(qpm, start_time, signals=None, channel=None) as sme:
        # functions can assume sme exists implicitly as closure
        # thus also giving implicit access to midi_hub, ect.
        # qpm =
        # TODO create midi events from / in-line-with metronome
        output_dir = "mag_out1"
        primer_midi = "data/primer.mid"
        SynGenModels.midi_prior_generates_midi_melody(primer_midi, output_dir)
        midi_data = get_midi_aggr_dir(output_dir)
        qpm = estimate_tempo(midi_data)
        before = sme.midi_hub._metronome.qpm
        sme.midi_hub._metronome.update(qpm=qpm, start_time=sme.start_time)
        after = sme.midi_hub._metronome.qpm
        print(f"BEFORE metronom qpm: {before}")
        print(f"AFTER metronom qpm: {after}")


class SynGenModels:

    @staticmethod
    def get_midi_str(primer_midi):
        output_dir = "/tmp/mag_tmp1.midi"
        SynGenModels.midi_prior_generates_midi_melody(primer_midi, output_dir)
        with open(output_dir, "r") as f:
            midi_bytes = f.readlines()
        return midi_bytes

    @staticmethod
    def midi_prior_generates_midi_melody(primer_midi, output_dir):
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
        bundle_path = "data/attention_rnn.mag"
        cmd = f"./generate-rnn-midi.sh {config} {bundle_path} {output_dir} {primer_midi}"
        subprocess.run(cmd, shell=True)


def test():
    primer_midi = "/Users/davisdulin/src/synaesthesia/synosc/data/primer.mid"
    # primer_melody = f"{[60]}"
    output_dir = "/tmp/mag_tmp2.midi"
    SynGenModels.midi_prior_generates_midi_melody(primer_midi, output_dir)


def main():
    test_cm()


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
