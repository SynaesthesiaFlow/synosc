from osc.osc_client import OscClient
from generators.models.melody_rnn import SynMelodyRNN
from utils.midi_util import get_midi_aggr_dir
import time


class SynOscClient(OscClient):

    def __init__(self, ip, port):
        OscClient.__init__(self, ip, port)

    def generate_messages(self):
        midi_fname = "/Users/davisdulin/src/synosc/data/primer.mid"
        mag_output_dir = "/Users/davisdulin/src/synosc/tmp"
        # SynMelodyRNN.midi_prior_generates_midi_melody(midi_fname, mag_output_dir)
        mag_out_f = "/Users/davisdulin/src/synosc/tmp/glob.midi"
        get_midi_aggr_dir(mag_output_dir, mag_out_f)
        with open(mag_out_f, "rb") as f:
            midi_data_str = f.readlines()
        print("midi_str: " + str(midi_data_str))
        self.client.send_message("/midi/0", [midi_data_str[0:30]])

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
