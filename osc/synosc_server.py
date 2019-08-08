import pretty_midi
import math
import logging

from osc.osc_server import OscServer
from generators.magenta_generator import synmagether

logger = logging.getLogger( __name__)


class SynOscServer(OscServer):
    def __init__(self, ip, port):
        OscServer.__init__(self, ip, port)

    def synthesize(self, unused_addr, args):
        # TODO take the midi file as an argument
        print(f"args: {args}")
        midi_fname = args
        midi_data = pretty_midi.PrettyMIDI(midi_fname)
        audio_data = midi_data.synthesize()
        print(f"audio_data: {audio_data}")
        # sd.play(audio_data, sps)
        return audio_data


    def receive_midi_str(self, unused_addr, args):
        print(f"args: {args}")


    @synmagether()
    def construct_dispatchers(self):
        self.dispatcher.map("/filter", print)
        self.dispatcher.map("/volume", self.print_volume_handler, "Volume")
        self.dispatcher.map("/logvolume", self.print_compute_handler, "Log volume", math.log)
        self.dispatcher.map("/midi/0", self.receive_midi_str)
        # self.dispatcher.map("/midi/1", self.magenta)
        return self


def build_server():
    server = OscServer("127.0.0.1", 5005)
    server.construct_dispatchers().start()


if __name__ == "__main__":
    build_server()
