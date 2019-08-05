import argparse
import math
import sounddevice as sd
from pythonosc import dispatcher
from pythonosc import osc_server
import pretty_midi
from osc_helper import OscObject
import osc_helper


class OscServer(OscObject):
    """
    Class for OSC Servers
    must override: construct_dispatchers()
    https://python-osc.readthedocs.io/en/latest/
    """

    def __init__(self, ip, port):
        OscObject.__init__(self, ip, port)
        self.ip = ip
        self.port = port
        self.dispatcher = dispatcher.Dispatcher()

    def construct_dispatchers(self):
        # override
        pass

    def start_server(self):
        """
        TODO: handle params to start different kinds of servers
        """
        server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), self.dispatcher)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()


class ExampleServer(OscServer):
    def __init__(self, ip, port):
        OscServer.__init__(self, ip, port)

    def print_volume_handler(self, unused_addr, args, volume):
        print("[{0}] ~ {1}".format(args[0], volume))

    def print_compute_handler(self, unused_addr, args, volume):
        try:
            print("[{0}] ~ {1}".format(args[0], args[1](volume)))
        except ValueError:
            pass

    def synthesize(self, unused_addr, args):
        # TODO take the midi file as an argument
        
        print(f"args: {args}")
        midi_fname = args
        midi_data = pretty_midi.PrettyMIDI(midi_fname)
        audio_data = midi_data.synthesize()
        print(f"audio_data: {audio_data}")
        return audio_data
        # sd.play(audio_data, sps)
    
    def receive_midi_str(self, unused_addr, args):
        print(f"args: {args}")

    def construct_dispatchers(self):
        self.dispatcher.map("/filter", print)
        self.dispatcher.map("/volume", self.print_volume_handler, "Volume")
        self.dispatcher.map("/logvolume", self.print_compute_handler, "Log volume", math.log)
        self.dispatcher.map("/midi/0", self.receive_midi_str)
        return self




def build_server():
    server = ExampleServer("127.0.0.1", 5005)
    server.construct_dispatchers().start_server()


if __name__ == "__main__":
    build_server()
