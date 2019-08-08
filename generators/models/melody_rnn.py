import subprocess


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
        cmd = f"./scrips/generate-rnn-midi.sh {config} {bundle_path} {output_dir} {primer_midi}"
        subprocess.run(cmd, shell=True)
