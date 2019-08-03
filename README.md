

Open Questions
    - what are the computational demands of an RNN vs a more advanced model like Coconet


TODO
    -  research to get your bearings
    -  create OSC and MIDI generators
    -  convert between the two
      -> use python_osc.Dispatcher to generate MIDI

Milestone
    - get noteSequence to Dispatch OSC message


Notes
    - magenta midi interface: https://github.com/tensorflow/magenta/tree/master/magenta/interfaces/midi
    - magenta ableton plugin
        - start by dragging magenta_studio amxd into ableton midi channel
          https://magenta.tensorflow.org/studio/ableton-live

Good Reads
    - https://magenta.tensorflow.org/mljam
        getting a machine learning model to play on beat and be stylistically consistent can be quite challenging
    - https://towardsdatascience.com/neural-networks-for-music-generation-97c983b50204
        Tonal Distance: measures the harmonicity between a pair of tracks. Larger tonal distance implies weaker inter-track harmonic relations.

Datasets
    - coconet
        https://github.com/czhuang/JSB-Chorales-dataset
        pre-trained checkpoints: http://download.magenta.tensorflow.org/models/coconet/checkpoint.zip

Versioning restrictions
    MidiOSC : OSX 10.5-10.11 and Ubuntu 9.10

