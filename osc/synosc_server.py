import pretty_midi
import logging

from generators.orchestrator import build_ether
from osc.osc_server import OscServer

logger = logging.getLogger( __name__)
ether = build_ether()


class SynOscServer(OscServer):
    def __init__(self, ether):
        ip = ether.muse.syn_config['default_ip']
        port = ether.muse.syn_config['default_port']
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

    def receive_midi_bytes(self, unused_addr, args):
        print(f"args: {args}")
        midi_bytes = args
        ether.muse.play_from_midi_mock(midi_bytes)

    def construct_dispatchers(self):
        self.dispatcher.map("/midi/0", self.receive_midi_bytes)
        # self.dispatcher.map("/midi/1", self.magenta)
        return self


def build_server():
    server = SynOscServer(ether)
    server = server.construct_dispatchers()
    server.start()


if __name__ == "__main__":
    build_server()
