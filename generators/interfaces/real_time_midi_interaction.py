import abc
import threading
import time
from absl import logging

import magenta
from magenta.protobuf import generator_pb2
from magenta.protobuf import music_pb2
import tensorflow as tf

from magenta.interfaces.midi.midi_interaction import MidiInteraction, adjust_sequence_times


class RealTimeMidiInteraction(MidiInteraction):
    """
    for reference, see: magenta/interfaces/midi/CallAndResponseMidiInteraction

    Implementation of a MidiInteraction for real-time interaction augmentation
     to complement what is played

    Starts by Listening quietly, then continuously plays generated sequences ('response')
    until user stops playing ('end_call_signal'), or placed in Idle state. The steady state
    continuously takes input and responds to it.

    MIDI Input and Output is through the MidiHub

    TODO Simplest transformations from existing processes:
        - Add state AUGMENT as a composition of simultaneous, indefinite "Call" and "Response" states
            - work in the same in/out chunks as CallAndResponse, but just have it be playing in response to the previous measure
            - Use existing MIDI IO for CallAndResponse.
                - midi_hub shouldn't change, threads allowing
        - have the Response play in a different mode: input(violin) -> output(drums, piano)
        - make in/out chunks smaller, while adding other forms of context into augmenter (latest, recent, historical)


    ------------------------------------------


    Alternates between receiving input from the MidiHub ("call") and playing
    generated sequences ("response"). During the call stage, the input is captured
    and used to generate the response, which is then played back during the
    response stage.

    The call phrase is started when notes are received and ended by an external
    signal (`end_call_signal`) or after receiving no note events for a full tick.
    The response phrase is immediately generated and played. Its length is
    optionally determined by a control value set for
    `response_ticks_control_number` or by the length of the call.

    Args:
      midi_hub: The MidiHub to use for MIDI I/O.
      sequence_generators: A collection of SequenceGenerator objects.
      qpm: The quarters per minute to use for this interaction. May be overriden
         by control changes sent to `tempo_control_number`.
      generator_select_control_number: An optional MIDI control number whose
         value to use for selection a sequence generator from the collection.
         Must be provided if `sequence_generators` contains multiple
         SequenceGenerators.
      clock_signal: An optional midi_hub.MidiSignal to use as a clock. Each tick
          period should have the same duration. No other assumptions are made
          about the duration, but is typically equivalent to a bar length. Either
          this or `tick_duration` must be specified.be
      tick_duration: An optional float specifying the duration of a tick period in
          seconds. No assumptions are made about the duration, but is typically
          equivalent to a bar length. Either this or `clock_signal` must be
          specified.
      end_call_signal: The optional midi_hub.MidiSignal to use as a signal to stop
          the call phrase at the end of the current tick.
      panic_signal: The optional midi_hub.MidiSignal to use as a signal to end
          all open notes and clear the playback sequence.
      mutate_signal: The optional midi_hub.MidiSignal to use as a signal to
          generate a new response sequence using the current response as the
          input.
      allow_overlap: A boolean specifying whether to allow the call to overlap
          with the response.
      metronome_channel: The optional 0-based MIDI channel to output metronome on.
          Ignored if `clock_signal` is provided.
      min_listen_ticks_control_number: The optional control change number to use
          for controlling the minimum call phrase length in clock ticks.
      max_listen_ticks_control_number: The optional control change number to use
          for controlling the maximum call phrase length in clock ticks. Call
          phrases will automatically be ended and responses generated when this
          length is reached.
      response_ticks_control_number: The optional control change number to use for
          controlling the length of the response in clock ticks.
      tempo_control_number: An optional MIDI control number whose value to use to
         determine the qpm for this interaction. On receipt of a control change,
         the qpm will be set to 60 more than the control change value.
      temperature_control_number: The optional control change number to use for
          controlling generation softmax temperature.
      loop_control_number: The optional control change number to use for
          determining whether the response should be looped. Looping is enabled
          when the value is 127 and disabled otherwise.
      state_control_number: The optinal control change number to use for sending
          state update control changes. The values are 0 for `IDLE`, 1 for
          `LISTENING`, and 2 for `RESPONDING`.

      Raises:
        ValueError: If exactly one of `clock_signal` or `tick_duration` is not
           specified.
    """

    class State(object):
        """
        Class holding state value representations.
        Same state names as CallAndResponse Interaction, but they are represented differently
        """
        IDLE = 0
        LISTENING = 1
        RESPONDING = 2
        AUGMENT = 3  # combines listening and responding into a single real-time response state

        _STATE_NAMES = {
            IDLE: 'Idle', LISTENING: 'Listening', RESPONDING: 'Responding', AUGMENT: 'Augment'}

        @classmethod
        def to_string(cls, state):
            return cls._STATE_NAMES[state]

    def __init__(self,
                 midi_hub,
                 sequence_generators,
                 qpm,
                 generator_select_control_number,
                 clock_signal=None,
                 tick_duration=None,
                 end_call_signal=None,
                 panic_signal=None,
                 mutate_signal=None,
                 allow_overlap=False,
                 metronome_channel=None,
                 min_listen_ticks_control_number=None,
                 max_listen_ticks_control_number=None,
                 response_ticks_control_number=None,
                 tempo_control_number=None,
                 temperature_control_number=None,
                 loop_control_number=None,
                 state_control_number=None):
        super(RealTimeMidiInteraction, self).__init__(
            midi_hub, sequence_generators, qpm, generator_select_control_number,
            tempo_control_number, temperature_control_number)
        if [clock_signal, tick_duration].count(None) != 1:
            raise ValueError(
                'Exactly one of `clock_signal` or `tick_duration` must be specified.')
        self._clock_signal = clock_signal
        self._tick_duration = tick_duration
        self._end_call_signal = end_call_signal
        self._panic_signal = panic_signal
        self._mutate_signal = mutate_signal
        self._allow_overlap = allow_overlap
        self._metronome_channel = metronome_channel
        self._min_listen_ticks_control_number = min_listen_ticks_control_number
        self._max_listen_ticks_control_number = max_listen_ticks_control_number
        self._response_ticks_control_number = response_ticks_control_number
        self._loop_control_number = loop_control_number
        self._state_control_number = state_control_number
        # Event for signalling when to end a call.
        self._end_call = threading.Event()
        # Event for signalling when to flush playback sequence.
        self._panic = threading.Event()
        # Even for signalling when to mutate response.
        self._mutate = threading.Event()

    def _update_state(self, state):
        """Logs and sends a control change with the state."""
        if self._state_control_number is not None:
            self._midi_hub.send_control_change(self._state_control_number, state)
        logging.info('State: %s', self.State.to_string(state))

    def _end_call_callback(self, unused_captured_seq):
        """Method to use as a callback for setting the end call signal."""
        self._end_call.set()
        logging.info('End call signal received.')

    def _panic_callback(self, unused_captured_seq):
        """Method to use as a callback for setting the panic signal."""
        self._panic.set()
        logging.info('Panic signal received.')

    def _mutate_callback(self, unused_captured_seq):
        """Method to use as a callback for setting the mutate signal."""
        self._mutate.set()
        logging.info('Mutate signal received.')

    @property
    def _min_listen_ticks(self):
        """Returns the min listen ticks based on the current control value."""
        val = self._midi_hub.control_value(
            self._min_listen_ticks_control_number)
        return 0 if val is None else val

    @property
    def _max_listen_ticks(self):
        """Returns the max listen ticks based on the current control value."""
        val = self._midi_hub.control_value(
            self._max_listen_ticks_control_number)
        return float('inf') if not val else val

    @property
    def _should_loop(self):
        return (self._loop_control_number and
                self._midi_hub.control_value(self._loop_control_number) == 127)

    def _generate(self, input_sequence, zero_time, response_start_time,
                  response_end_time):
        """Generates a response sequence with the currently-selected generator.

        Args:
          input_sequence: The NoteSequence to use as a generation seed.
          zero_time: The float time in seconds to treat as the start of the input.
          response_start_time: The float time in seconds for the start of
              generation.
          response_end_time: The float time in seconds for the end of generation.

        Returns:
          The generated NoteSequence.
        """
        # Generation is simplified if we always start at 0 time.
        response_start_time -= zero_time
        response_end_time -= zero_time

        generator_options = generator_pb2.GeneratorOptions()
        generator_options.input_sections.add(
            start_time=0,
            end_time=response_start_time)
        generator_options.generate_sections.add(
            start_time=response_start_time,
            end_time=response_end_time)

        # Get current temperature setting.
        generator_options.args['temperature'].float_value = self._temperature

        # Generate response.
        logging.info(
            "Generating sequence using '%s' generator.",
            self._sequence_generator.details.id)
        logging.debug('Generator Details: %s',
                         self._sequence_generator.details)
        logging.debug('Bundle Details: %s',
                         self._sequence_generator.bundle_details)
        logging.debug('Generator Options: %s', generator_options)
        response_sequence = self._sequence_generator.generate(
            adjust_sequence_times(input_sequence, -zero_time), generator_options)
        response_sequence = magenta.music.trim_note_sequence(
            response_sequence, response_start_time, response_end_time)
        return adjust_sequence_times(response_sequence, zero_time)

    def run(self):
        """The main loop for a real-time call and response interaction.

        Breakdown:
            input: MidiCaptor: Base class thread captures MIDI into a NoteSequence proto. (PolyphonicMidiCaptor, MonophonicMidiCaptor)
            output: MIDIPlayer (player): Plays the notes in aNoteSequence via the MIDI output port

        Approaches:
            - need to be able to mock inputs/outputs to test my changes
                - sounddevice? hi-jack the midi ports and play em back with sounddevice, avoiding needing ableton or similar integration
                - but maybe there's an easy software for working with the IAC Bus Drivers whatever?
                - hook up virtual MIDI bus to ableton?
                    https://help.ableton.com/hc/en-us/articles/209774225-How-to-setup-a-virtual-MIDI-bus
        """
        start_time = time.time()
        self._captor = self._midi_hub.start_capture(self._qpm, start_time)

        if not self._clock_signal and self._metronome_channel is not None:
            self._midi_hub.start_metronome(
                self._qpm, start_time, channel=self._metronome_channel)

        # Set callback for end call signal.
        if self._end_call_signal is not None:
            self._captor.register_callback(self._end_call_callback,
                                           signal=self._end_call_signal)
        if self._panic_signal is not None:
            self._captor.register_callback(self._panic_callback,
                                           signal=self._panic_signal)
        if self._mutate_signal is not None:
            self._captor.register_callback(self._mutate_callback,
                                           signal=self._mutate_signal)

        # Keep track of the end of the previous tick time.
        last_tick_time = time.time()

        # Keep track of the duration of a listen state.
        listen_ticks = 0

        # Start with an empty response sequence.
        response_sequence = music_pb2.NoteSequence()
        response_start_time = 0
        response_duration = 0
        player = self._midi_hub.start_playback(
            response_sequence, allow_updates=True)

        # Enter loop at each clock tick.
        for captured_sequence in self._captor.iterate(signal=self._clock_signal,
                                                      period=self._tick_duration):
            if self._stop_signal.is_set():
                break
            if self._panic.is_set():
                response_sequence = music_pb2.NoteSequence()
                player.update_sequence(response_sequence)
                self._panic.clear()

            tick_time = captured_sequence.total_time

            # Set to current QPM, since it might have changed.
            if not self._clock_signal and self._metronome_channel is not None:
                self._midi_hub.start_metronome(
                    self._qpm, tick_time, channel=self._metronome_channel)
            captured_sequence.tempos[0].qpm = self._qpm

            tick_duration = tick_time - last_tick_time
            if captured_sequence.notes:
                last_end_time = max(note.end_time for note in captured_sequence.notes)
            else:
                last_end_time = 0.0

            # True iff there was no input captured during the last tick.
            silent_tick = last_end_time <= last_tick_time

            if not silent_tick:
                listen_ticks += 1

            if not captured_sequence.notes:
                # Reset captured sequence since we are still idling.
                if response_sequence.total_time <= tick_time:
                    self._update_state(self.State.IDLE)
                if self._captor.start_time < tick_time:
                    self._captor.start_time = tick_time
                self._end_call.clear()
                listen_ticks = 0
            elif (self._end_call.is_set() or
                  silent_tick or
                  listen_ticks >= self._max_listen_ticks):
                if listen_ticks < self._min_listen_ticks:
                    logging.info(
                        'Input too short (%d vs %d). Skipping.',
                        listen_ticks,
                        self._min_listen_ticks)
                    self._captor.start_time = tick_time
                else:
                    # Create response and start playback.
                    self._update_state(self.State.RESPONDING)

                    capture_start_time = self._captor.start_time

                    if silent_tick:
                        # Move the sequence forward one tick in time.
                        captured_sequence = adjust_sequence_times(
                            captured_sequence, tick_duration)
                        captured_sequence.total_time = tick_time
                        capture_start_time += tick_duration

                    # Compute duration of response.
                    num_ticks = self._midi_hub.control_value(
                        self._response_ticks_control_number)

                    if num_ticks:
                        response_duration = num_ticks * tick_duration
                    else:
                        # Use capture duration.
                        response_duration = tick_time - capture_start_time

                    response_start_time = tick_time
                    response_sequence = self._generate(
                        captured_sequence,
                        capture_start_time,
                        response_start_time,
                        response_start_time + response_duration)

                    # If it took too long to generate, push response to next tick.
                    if (time.time() - response_start_time) >= tick_duration / 4:
                        push_ticks = (
                                (time.time() - response_start_time) // tick_duration + 1)
                        response_start_time += push_ticks * tick_duration
                        response_sequence = adjust_sequence_times(
                            response_sequence, push_ticks * tick_duration)
                        logging.warn(
                            'Response too late. Pushing back %d ticks.', push_ticks)

                    # Start response playback. Specify the start_time to avoid stripping
                    # initial events due to generation lag.
                    player.update_sequence(
                        response_sequence, start_time=response_start_time)

                    # Optionally capture during playback.
                    if self._allow_overlap:
                        self._captor.start_time = response_start_time
                    else:
                        self._captor.start_time = response_start_time + response_duration

                # Clear end signal and reset listen_ticks.
                self._end_call.clear()
                listen_ticks = 0
            else:
                # Continue listening.
                self._update_state(self.State.LISTENING)

            # Potentially loop or mutate previous response.
            if self._mutate.is_set() and not response_sequence.notes:
                self._mutate.clear()
                logging.warn('Ignoring mutate request with nothing to mutate.')

            if (response_sequence.total_time <= tick_time and
                    (self._should_loop or self._mutate.is_set())):
                if self._mutate.is_set():
                    new_start_time = response_start_time + response_duration
                    new_end_time = new_start_time + response_duration
                    response_sequence = self._generate(
                        response_sequence,
                        response_start_time,
                        new_start_time,
                        new_end_time)
                    response_start_time = new_start_time
                    self._mutate.clear()

                response_sequence = adjust_sequence_times(
                    response_sequence, tick_time - response_start_time)
                response_start_time = tick_time
                player.update_sequence(
                    response_sequence, start_time=tick_time)

            last_tick_time = tick_time

        player.stop()

    def stop(self):
        self._stop_signal.set()
        self._captor.stop()
        self._midi_hub.stop_metronome()
        super(RealTimeMidiInteraction, self).stop()
