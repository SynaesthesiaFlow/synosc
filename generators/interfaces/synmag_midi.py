"""A MIDI interface to the sequence generators.

Captures monophonic input MIDI sequences and plays back responses from the
sequence generator.

TODO: upgrade to Tensorflow 2.0   https://www.tensorflow.org/beta/guide/effective_tf2

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import re
import threading
import time
import os
from absl import logging


import magenta
from magenta.interfaces.midi import midi_hub
from magenta.interfaces.midi import midi_interaction
from magenta.models.drums_rnn import drums_rnn_sequence_generator
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.performance_rnn import performance_sequence_generator
from magenta.models.pianoroll_rnn_nade import pianoroll_rnn_nade_sequence_generator
from magenta.models.polyphony_rnn import polyphony_sequence_generator
import tensorflow as tf

from generators.interfaces.real_time_midi_interaction import RealTimeMidiInteraction

"""
change log:
input_ports(magenta_in) -> input_ports(synmag_in)
"""


default_midi_config = {
    "list_ports": False,
    "input_ports": "synmag_in",
    "output_ports": "magenta_out",
    "passthrough": True,
    "clock_control_number": None,
    "end_call_control_number": None,
    "panic_control_number": None,
    "mutate_control_number": None,
    "min_listen_ticks_control_number": None,
    "max_listen_ticks_control_number": None,
    "response_ticks_control_number": None,
    "temperature_control_number": None,
    "allow_overlap": False,
    "enable_metronome": True,
    "metronome_channel": 1,
    "qpm": 120,
    "tempo_control_number": None,
    "loop_control_number": None,
    "bundle_files": None,
    "generator_select_control_number": None,
    "state_control_number": None,
    "playback_offset": 0.0,
    "playback_channel": 0,
    "learn_controls": False,
    "log": "WARN",
    "real_time_midi": False,
}

_CONTROL_FLAGS = [
    "clock_control_number",
    "end_call_control_number",
    "panic_control_number",
    "mutate_control_number",
    "min_listen_ticks_control_number",
    "max_listen_ticks_control_number",
    "response_ticks_control_number",
    "temperature_control_number",
    "tempo_control_number",
    "loop_control_number",
    "generator_select_control_number",
    "state_control_number",
]

# A map from a string generator name to its class.
_GENERATOR_MAP = melody_rnn_sequence_generator.get_generator_map()
_GENERATOR_MAP.update(drums_rnn_sequence_generator.get_generator_map())
_GENERATOR_MAP.update(performance_sequence_generator.get_generator_map())
_GENERATOR_MAP.update(pianoroll_rnn_nade_sequence_generator.get_generator_map())
_GENERATOR_MAP.update(polyphony_sequence_generator.get_generator_map())


class CCMapper(object):
    """A class for mapping control change numbers to specific controls.

  Args:
    cc_map: A dictionary containing mappings from signal names to control
        change numbers (or None). This dictionary will be updated by the class.
    midi_hub_: An initialized MidiHub to receive inputs from.
  """

    def __init__(self, cc_map, midi_hub_):
        self._cc_map = cc_map
        self._signals = cc_map.keys()
        self._midi_hub = midi_hub_
        self._update_event = threading.Event()

    def _print_instructions(self):
        """Prints instructions for mapping control changes."""
        print(
            "Enter the index of a signal to set the control change for, or `q` "
            "when done."
        )
        fmt = "{:>6}\t{:<20}\t{:>6}"
        print(fmt.format("Index", "Control", "Current"))
        for i, signal in enumerate(self._signals):
            print(fmt.format(i + 1, signal, self._cc_map.get(signal)))
        print("")

    def _update_signal(self, signal, msg):
        """Updates mapping for the signal to the message's control change.

    Args:
      signal: The name of the signal to update the control change for.
      msg: The mido.Message whose control change the signal should be set to.
    """
        if msg.control in self._cc_map.values():
            print("Control number %d is already assigned. Ignoring." % msg.control)
        else:
            self._cc_map[signal] = msg.control
            print("Assigned control number %d to `%s`." % (msg.control, signal))
        self._update_event.set()

    def update_map(self):
        """Enters a loop that receives user input to set signal controls."""
        while True:
            print("")
            self._print_instructions()
            response = input("Selection: ")
            if response == "q":
                return
            try:
                signal = self._signals[int(response) - 1]
            except (ValueError, IndexError):
                print("Invalid response:", response)
                continue
            self._update_event.clear()
            self._midi_hub.register_callback(
                functools.partial(self._update_signal, signal),
                midi_hub.MidiSignal(type="control_change"),
            )
            print(
                "Send a control signal using the control number you wish to "
                "associate with `%s`." % signal
            )
            self._update_event.wait()


def _validate_midi_config(midi_config):
    """Returns True if flag values are valid or prints error and returns False."""
    if midi_config["list_ports"]:
        print("Input ports: '%s'" % ("', '".join(midi_hub.get_available_input_ports())))
        print(
            "Ouput ports: '%s'" % ("', '".join(midi_hub.get_available_output_ports()))
        )
        return False

    if midi_config["bundle_files"] is None:
        print("--bundle_files must be specified.")
        return False

    if (
        len(midi_config["bundle_files"].split(",")) > 1
        and midi_config['generator_select_control_number'] is None
    ):
        logging.warning(
            "You have specified multiple bundle files (generators), without "
            "setting `--generator_select_control_number`. You will only be able to "
            "use the first generator (%s).",
            midi_config["bundle_files"][0],
        )

    return True


def _load_generator_from_bundle_file(bundle_file):
    """Returns initialized generator from bundle file path or None if fails."""
    try:
        bundle = magenta.music.sequence_generator_bundle.read_bundle_file(bundle_file)
    except magenta.music.sequence_generator_bundle.GeneratorBundleParseError:
        print("Failed to parse bundle file: %s" % default_midi_config["bundle_file"])
        return None

    generator_id = bundle.generator_details.id
    if generator_id not in _GENERATOR_MAP:
        print(
            "Unrecognized SequenceGenerator ID '%s' in bundle file: %s"
            % (generator_id, default_midi_config["bundle_file"])
        )
        return None

    generator = _GENERATOR_MAP[generator_id](checkpoint=None, bundle=bundle)
    generator.initialize()
    print(
        "Loaded '%s' generator bundle from file '%s'."
        % (bundle.generator_details.id, bundle_file)
    )
    return generator


def _print_instructions():
    """Prints instructions for interaction based on the flag values."""
    print("")
    print("Instructions:")
    print("Start playing  when you want to begin the call phrase.")
    if default_midi_config['end_call_control_number'] is not None:
        print(
            "When you want to end the call phrase, signal control number %d "
            "with value 127, or stop playing and wait one clock tick."
            % default_midi_config['end_call_control_number']
        )
    else:
        print(
            "When you want to end the call phrase, stop playing and wait one "
            "clock tick."
        )
    print(
        "Once the response completes, the interface will wait for you to "
        "begin playing again to start a new call phrase."
    )
    print("")
    print("To end the interaction, press CTRL-C.")


def get_real_time_midi_interaction(
    hub,
    generators,
    clock_signal,
    tick_duration,
    end_call_signal,
    panic_signal,
    mutate_signal,
    metronome_channel,
    control_map,
):
    return RealTimeMidiInteraction(
        hub,
        generators,
        default_midi_config["qpm"],
        default_midi_config['generator_select_control_number'],
        clock_signal=clock_signal,
        tick_duration=tick_duration,
        end_call_signal=end_call_signal,
        panic_signal=panic_signal,
        mutate_signal=mutate_signal,
        allow_overlap=default_midi_config["allow_overlap"],
        metronome_channel=metronome_channel,
        min_listen_ticks_control_number=control_map["min_listen_ticks"],
        max_listen_ticks_control_number=control_map["max_listen_ticks"],
        response_ticks_control_number=control_map["response_ticks"],
        tempo_control_number=control_map["tempo"],
        temperature_control_number=control_map["temperature"],
        loop_control_number=control_map["loop"],
        state_control_number=control_map["state"],
    )


def get_call_and_response_midi_interaction(
    hub,
    generators,
    clock_signal,
    tick_duration,
    end_call_signal,
    panic_signal,
    mutate_signal,
    metronome_channel,
    control_map,
):
    return midi_interaction.CallAndResponseMidiInteraction(
        hub,
        generators,
        default_midi_config["qpm"],
        default_midi_config['generator_select_control_number'],
        clock_signal=clock_signal,
        tick_duration=tick_duration,
        end_call_signal=end_call_signal,
        panic_signal=panic_signal,
        mutate_signal=mutate_signal,
        allow_overlap=default_midi_config["allow_overlap"],
        metronome_channel=metronome_channel,
        min_listen_ticks_control_number=control_map["min_listen_ticks"],
        max_listen_ticks_control_number=control_map["max_listen_ticks"],
        response_ticks_control_number=control_map["response_ticks"],
        tempo_control_number=control_map["tempo"],
        temperature_control_number=control_map["temperature"],
        loop_control_number=control_map["loop"],
        state_control_number=control_map["state"],
    )


def get_piano_mag_paths():
    """
    candidate piano mags: ["./basic_rnn.mag", "./lookback_rnn.mag", "./attention_rnn.mag","./rl_rnn.mag", "./polyphony_rnn.mag", "./pianoroll_rnn_nade.mag"]
    :return: path to piano mags
    """

    return os.path.join(os.environ['SYNOSC_PATH'], "data", "mags", "attention_rnn.mag")


def get_drum_mag_path():
    """
    :return: path to drum mag
    """
    return os.path.join(os.environ['SYNOSC_PATH'], "data", "mags", "drum_kit_rnn.mag")


def run_default_drums():
    """
    replaces the RUN_DEMO.sh script from ai-ableton-jam
    """
    drum_mag_path = get_drum_mag_path()
    default_drums_default_midi_config = {
        "input_ports": "IAC Driver IAC Bus 3",
        "output_ports": "IAC Driver IAC Bus 4",
        "passthrough": False,
        "qpm": 120,
        "allow_overlap": True,
        "enable_metronome": False,
        "clock_control_number": 1,
        "end_call_control_number": 2,
        "min_listen_ticks_control_number": 3,
        "max_listen_ticks_control_number": 4,
        "response_ticks_control_number": 5,
        "temperature_control_number": 6,
        "tempo_control_number": 7,
        "generator_select_control_number": 8,
        "state_control_number": 9,
        "loop_control_number": 10,
        "panic_control_number": 11,
        "mutate_control_number": 12,
        "bundle_files": drum_mag_path,
        "playback_offset": -0.035,
        "playback_channel": 2,
        "log": "INFO"
    }

    drums_config = default_midi_config.copy()
    drums_config.update(default_drums_default_midi_config)
    runner(drums_config)


def run_default_piano():
    """
    replaces the RUN_DEMO.sh script from ai-ableton-jam
    """
    mag_bundle = get_piano_mag_paths()
    default_piano_default_midi_config = {
            "input_ports": "IAC Driver IAC Bus 1",
            "output_ports": "IAC Driver IAC Bus 2",
            "passthrough": False,
            "qpm": 120,
            "allow_overlap": True,
            "enable_metronome": False,
            "log": "DEBUG",
            "clock_control_number": 1,
            "end_call_control_number": 2,
            "min_listen_ticks_control_number": 3,
            "max_listen_ticks_control_number": 4,
            "response_ticks_control_number": 5,
            "temperature_control_number": 6,
            "tempo_control_number": 7,
            "generator_select_control_number": 8,
            "state_control_number": 9,
            "loop_control_number": 10,
            "panic_control_number": 11,
            "mutate_control_number": 12,
            "bundle_files": mag_bundle,
            "playback_offset": -0.035,
            "playback_channel": "1&"
    }

    piano_config = default_midi_config.copy()
    piano_config.update(default_piano_default_midi_config)
    runner(piano_config)


def runner(midi_config):
    logging.set_verbosity(midi_config['log'])

    if not _validate_midi_config(midi_config):
        return

    # Load generators.
    generators = []
    for bundle_file in midi_config['bundle_files'].split(","):
        generators.append(_load_generator_from_bundle_file(bundle_file))
        if generators[-1] is None:
            return

    # Initialize MidiHub.
    hub = midi_hub.MidiHub(
        midi_config["input_ports"].split(","),
        midi_config["output_ports"].split(","),
        midi_hub.TextureType.POLYPHONIC,
        passthrough=midi_config['passthrough'],
        playback_channel=midi_config["playback_channel"],
        playback_offset=midi_config["playback_offset"],
    )

    control_map = {
        re.sub("_control_number$", "", f): midi_config[f] for f in _CONTROL_FLAGS
    }
    if midi_config["learn_controls"]:
        CCMapper(control_map, hub).update_map()

    if control_map["clock"] is None:
        # Set the tick duration to be a single bar, assuming a 4/4 time signature.
        clock_signal = None
        tick_duration = 4 * (60.0 / midi_config["qpm"])
    else:
        clock_signal = midi_hub.MidiSignal(control=control_map["clock"], value=127)
        tick_duration = None

    def _signal_from_control_map(name):
        if control_map[name] is None:
            return None
        return midi_hub.MidiSignal(control=control_map[name], value=127)

    end_call_signal = _signal_from_control_map("end_call")
    panic_signal = _signal_from_control_map("panic")
    mutate_signal = _signal_from_control_map("mutate")
    metronome_channel = (
        midi_config["metronome_channel"] if midi_config["enable_metronome"] else None
    )
    if midi_config["real_time_midi"]:
        interaction = get_real_time_midi_interaction(
            hub,
            generators,
            clock_signal,
            tick_duration,
            end_call_signal,
            panic_signal,
            mutate_signal,
            metronome_channel,
            control_map,
        )
    else:
        interaction = get_call_and_response_midi_interaction(
            hub,
            generators,
            clock_signal,
            tick_duration,
            end_call_signal,
            panic_signal,
            mutate_signal,
            metronome_channel,
            control_map,
        )
    _print_instructions()
    interaction.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        interaction.stop()

    print("Interaction stopped.")


def real_time_midi():
    pass


def console_entry_point():
    """
    Thinkin outloud and th
        - failing because flag params are being passed to calling function?

    NEXT: how to interface with the MIDI runner?
            - I think i need to look into the max4live patch and the ableton set

    :return:
    """
    thread1 = threading.Thread(target=run_default_drums)
    thread1.start()
    thread2 = threading.Thread(target=run_default_piano)
    thread2.start()


if __name__ == "__main__":
    # execute as TF app when ran as main
    # have entry point for non-TF app (or TF app that is just started elsewhere?
    # i'm not really sure what
    console_entry_point()
