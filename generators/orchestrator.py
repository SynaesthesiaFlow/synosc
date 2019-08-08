"""
Orchestrator combines generative contexts
to be point of contact for OSC Dispatchers
calls interface to send OSC Client messages

scaffold to help encode dependency/parameter injection

Problems/Difficulties:
    - threading midi channels
        thought: have different interpreters for each midi channel
"""

from generators.magenta_generator import GenerativeMusicScene
from generators.lx_generator import GenerativeLightScene
from generators.models.melody_rnn import SynMelodyRNN


def main():
    audio_gen_muse = SynMelodyRNN()
    muse = GenerativeMusicScene(audio_gen_muse)
    rah = GenerativeLightScene()


if __name__ == "__main__":
    main()
