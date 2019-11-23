"""

Improv RNN
    This model generates melodies a la Melody RNN, but conditions the melodies on an underlying chord progression.
    At each step of generation, the model is also given the current chord as input (encoded as a vector).
    Instead of training on MIDI files, the model is trained on lead sheets in MusicXML format.



Compare models for candidate base:
    - Polyphony_RNN
    - drums_rnn
models to read:
    - arbitrary_image_stylization
    - image_stylization
    -  
"""