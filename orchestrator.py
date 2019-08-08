"""
goals:
    - run gen scene thread along with osc server thread
    - this is a good place to start exposing relevant parameters

OSC Client is a thread that constantly polls a dir for new midi file to play

TODO
    - learn about threads in different osc server types
    - debug and cleanup GenerativeScene
"""

from magenta_helper import GenerativeMusicScene
from osc_server import SynOscServer
from osc_client import SynOscClient


def build_server():
    server = SynOscServer("127.0.0.1", 5005)
    server.construct_dispatchers().start()


def start_client_poll():
    pass


def start():
    """
    :return: 
    """
    build_server()
    print("build server thread")
    gen_scene = GenerativeMusicScene()
    gen_scene.start()
    print("running gen scene")
    start_client_poll()
    print("STILL HAVE THREAD TO RUN STUFF")
    print("SETUP ACCESS POINTS TO PREVIOUS THREADS")


if __name__ == "__main__":
    start()
