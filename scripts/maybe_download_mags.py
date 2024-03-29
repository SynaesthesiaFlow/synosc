"""
get moar mags:
    https://github.com/tensorflow/magenta-demos/tree/master/ai-jam-ableton#download-bundles-pretrained-models
"""
import os
from urllib.request import URLopener

# This script downloads these .mag files if not already present.
mag_files = [
    'http://download.magenta.tensorflow.org/models/attention_rnn.mag',
    'http://download.magenta.tensorflow.org/models/performance.mag',
    'http://download.magenta.tensorflow.org/models/pianoroll_rnn_nade.mag',
    'http://download.magenta.tensorflow.org/models/drum_kit_rnn.mag',
]

for mag_file in mag_files:
  output_file = mag_file.split('/')[-1]
  if os.path.exists(output_file):
    print('File %s already present' % mag_file)
  else:
    print('Writing %s to %s' % (mag_file, output_file))
    urlopener = URLopener()
    urlopener.retrieve(mag_file, output_file)