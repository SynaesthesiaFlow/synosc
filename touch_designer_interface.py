"""
Notes for Integrating with Touch Designer

TODO
    - what would a mocked TD interface look like? my guess is an osc_helper.Hanlder

Open Questions
    - osc schema definitions
    - osc schema constraints?
        - is there an implied schema when plugging something (like a midi channel) into ableton?
    - do we want to go for some kind of direct mapping between an instrument -> magenta -> LXEngine?
    - which features do we want to expose from magenta?
        - call & response (melody_rnn, coconet, ...)
        - compliment/augment in real time
            - camouflage latency by requiring inertia behind rhythm/harmony?
        - it would be nice if there was a word-movers-distance equivalent to filling up frequency space with complimentary harmonies

Interface with TouchDesigner
    - schema intentions: simple, extensible
    - Inbound: synosc should be able to automatically capture as much as possible, as simply as possible, through some pre-defined schema
        - midi controllers
            - is there a schema spec for this type of osc message/bundle
        - ableton configs
            - anything to gleam
        - LX Pattern state (Java)

        Inbound Schema Draft:
        {
            midi_channel: int,
            midi_data/0-n: (str) instruments,
            exposed_magenta_params: {
                melody_rnn:
                    playback_length: int
            }
            exposed_mir_params: json

        }

    - Outbound:
        - osc(midi)
            - different schema spec for this message/bundle? it should have a place for metadata resulting from processing
        - aggregate features and prioritize
            - real-time consonance / dissonance classifier
            - mir_eval.beat.continuity (is the rhythm consistent?)

        Outbound Schema Draft:
        {
            midi_data: byte_str
            metadata: {
                key_estimate: str,
                beat estimate: float,
                continuity_estimate
            }
        }



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

speech analysis? https://github.com/tyiannak/pyAudioAnalysis


"""