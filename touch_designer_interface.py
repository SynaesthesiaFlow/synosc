"""
Notes for Integrating with Touch Designer

Open Questions
    - osc schema definitions
    - osc schema constraints?
        - is there an implied schema when plugging something (like a midi channel) into ableton?


Interface with TouchDesigner
    - schema intentions: simple, extensible
    - Inbound: synosc should be able to automatically capture as much as possible, as simply as possible, through some pre-defined schema
        https://github.com/ideoforms/pylive/blob/master/examples/ex-live-scan.py
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


Other libraries of potential interest:
    PyLive: Query and control Ableton Live from Python (built on LiveOSC and liblo)
        https://github.com/ideoforms/pylive/tree/master/examples
    max4Live connection kit
        https://github.com/Ableton/m4l-connection-kit
        Touch OSC: https://github.com/Ableton/m4l-connection-kit/tree/master/OSC%20TouchOSC
    LiveOSC2: MIDI remote script for communication with Ableton Live over OSC
        https://github.com/stufisher/LiveOSC2
        looks old, use TouchDesigner instead

"""