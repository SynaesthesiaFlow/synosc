#!/usr/bin/env bash

# download maxpat: https://github.com/tensorflow/magenta-demos/tree/master/ai-jam-ableton#download-max-patches
# download als: https://github.com/tensorflow/magenta-demos/tree/master/ai-jam-ableton#download-live-set
#open NIPS_2016_Demo.als
#open magenta_mira.maxpat

python "$SYNOSC_PATH/generators/interfaces/synmag_midi.py"
