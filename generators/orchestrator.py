"""
Orchestrator combines generative contexts
scaffold to help encode dependency/parameter injection
"""

from generators.magenta_generator import GenerativeMusicScene
from generators.lx_generator import GenerativeLightScene


def main():
    muse = GenerativeMusicScene()
    rah = GenerativeLightScene()


if __name__ == "__main__":
    main()
