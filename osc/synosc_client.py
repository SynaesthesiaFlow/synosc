import random

from osc.osc_client import OscClient
from generators.models.melody_rnn import SynMelodyRNN

class SynOscClient(OscClient):

    def __init__(self, ip, port):
        OscClient.__init__(self, ip, port)

    def generate_messages(self):
        midi_fname = "data/primer.mid"
        client = self.get_udp_client()
        client.send_message("/volume", 1)
        client.send_message("/filter", random.random())
        # call magenta to create midi
        mag_output_dir = "/tmp/melody_rnn/generated"
        SynMelodyRNN.midi_prior_generates_midi_melody(midi_fname, mag_output_dir)
        with open(mag_output_dir, "rb") as f:
            midi_data_str = f.readlines()
        client.send_message("/midi/0", [midi_data_str])



def build_client():
    client = SynOscClient("127.0.0.1", 5005)
    client.generate_messages()


if __name__ == "__main__":
    build_client()
