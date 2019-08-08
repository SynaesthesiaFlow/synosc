from osc.osc_client import OscClient
from generators.models.melody_rnn import SynMelodyRNN
from utils.wrench import get_abs_fnames_in_dir
import os

class SynOscClient(OscClient):

    MAX_PACKET = 9200  # length of bytes http://opensoundcontrol.org/topic/247

    def __init__(self, ip, port):
        OscClient.__init__(self, ip, port)

    def generate_messages(self):
        midi_fname = "/Users/davisdulin/src/synosc/data/primer.mid"
        mag_output_dir = "/Users/davisdulin/src/synosc/tmp/data"
        SynMelodyRNN.midi_prior_generates_midi_melody(midi_fname, mag_output_dir)
        out_dir = os.path.join(os.path.dirname(__file__), "..", "tmp", "data")
        self.send_midi_dir(out_dir)

    def send_midi_dir(self, out_midi_dir):
        for midi_file in get_abs_fnames_in_dir(out_midi_dir):
            with open(midi_file, "rb") as f:
                midi_bytes = f.read()
                self.client.send_message("/midi/0", [midi_bytes])
            break
    # def build_bundle(self):
    #     bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    #     msg = osc_message_builder.OscMessageBuilder(address="/SYNC")
    #     msg.add_arg(4.0)
    #     # Add 4 messages in the bundle, each with more arguments.
    #     bundle.add_content(msg.build())
    #     msg.add_arg(2)
    #     bundle.add_content(msg.build())
    #     msg.add_arg("value")
    #     bundle.add_content(msg.build())
    #     msg.add_arg(b"\x01\x02\x03")
    #     bundle.add_content(msg.build())
    #
    #     sub_bundle = bundle.build()
    #     # Now add the same bundle inside itself.
    #     bundle.add_content(sub_bundle)
    #     # The bundle has 5 elements in total now.
    #
    #     bundle = bundle.build()
    #     # You can now send it via a client as described in other examples.




def build_client():
    client = SynOscClient("127.0.0.1", 5005)
    client.generate_messages()


if __name__ == "__main__":
    build_client()
