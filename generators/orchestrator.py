"""
Orchestrator loads and combines generative contexts

integrate with metronome

Problems/Difficulties:
    - threading midi channels
        thought: have different interpreters for each midi channel
"""


from generators.music_generator import GenerativeMusicScene
from generators.light_generator import GenerativeLightScene
from utils.wrench import get_syn_config


class Ether:
    def __init__(self):
        self.syn_config = get_syn_config()

        self.muse = GenerativeMusicScene(self.syn_config)
        self.rah = GenerativeLightScene()



def build_ether():
    return Ether()


def main():
    build_ether()


if __name__ == "__main__":
    main()
