

# Open Questions
    - what are our infrasound installations?
    
# TODO
    - need to integrate the IAC Driver IAC Bus 1-4 in with ableton
        - use max4live patch and AbletonLiveSet
             maxpat: https://github.com/tensorflow/magenta-demos/tree/master/ai-jam-ableton#download-max-patches
             als: https://github.com/tensorflow/magenta-demos/tree/master/ai-jam-ableton#download-live-set

# Other, less important Questions
    - what are the computational demands of a vanilla RNN vs something like Coconet
    - is any of this tooling useful?
        - TouchDesigner substitute? https://osculator.net/
        - https://www.ableton.com/en/packs/connection-kit/

# Notes
    - magenta midi interface: https://github.com/tensorflow/magenta/tree/master/magenta/interfaces/midi
    - magenta ableton plugin
        - start by dragging magenta_studio amxd into ableton midi channel
          https://magenta.tensorflow.org/studio/ableton-live

# Resources
    - Deep Learning for Audio
        https://forums.fast.ai/t/deep-learning-with-audio-thread/38123?fbclid=IwAR3kdKKsroTnwA2h1xzf4zvOGzdUh1aL1RxTXUCrWtqccGnBx6zSdDcdOYM
    - Notes on Music Information Retrieval (w/ ipynbs)
        https://musicinformationretrieval.com/index.html

# Reads
    - https://magenta.tensorflow.org/mljam
        getting a machine learning model to play on beat and be stylistically consistent can be quite challenging
    - https://towardsdatascience.com/neural-networks-for-music-generation-97c983b50204
        Tonal Distance: measures the harmonicity between a pair of tracks. Larger tonal distance implies weaker inter-track harmonic relations.

# Datasets
    - coconet
        - https://github.com/czhuang/JSB-Chorales-dataset
        - pre-trained checkpoints: http://download.magenta.tensorflow.org/models/coconet/checkpoint.zip

# Installation
    - export PYTHONPATH=$PYTHONPATH:/path/to/synosc
    - clone magenta and START READING
    