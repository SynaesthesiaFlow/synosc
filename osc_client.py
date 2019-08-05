from osc_helper import OscObject
import pretty_midi
from pythonosc import udp_client
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
import osc_helper
import random


class OscClient(OscObject):
    """
    Class for OSC Clients
    must override: generate_messages()
    https://python-osc.readthedocs.io/en/latest/
    """

    def __init__(self, ip, port):
        OscObject.__init__(self, ip, port)
        self.ip = ip
        self.port = port

    def generate_messages(self):
        # override
        pass

    def get_udp_client(self):
        client = udp_client.SimpleUDPClient(self.ip, self.port)
        return client

    def generate_bundles(self):
        # TODO learn about bundles
        pass

    def build_bundle(self):
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        msg = osc_message_builder.OscMessageBuilder(address="/SYNC")
        msg.add_arg(4.0)
        # Add 4 messages in the bundle, each with more arguments.
        bundle.add_content(msg.build())
        msg.add_arg(2)
        bundle.add_content(msg.build())
        msg.add_arg("value")
        bundle.add_content(msg.build())
        msg.add_arg(b"\x01\x02\x03")
        bundle.add_content(msg.build())

        sub_bundle = bundle.build()
        # Now add the same bundle inside itself.
        bundle.add_content(sub_bundle)
        # The bundle has 5 elements in total now.

        bundle = bundle.build()
        # You can now send it via a client as described in other examples.


class ExampleClient(OscClient):

    def __init__(self, ip, port):
        OscClient.__init__(self, ip, port)

    def generate_messages(self):
        midi_fname = "data/primer.mid"
        client = self.get_udp_client()
        client.send_message("/volume", 1)
        client.send_message("/filter", random.random())
        # TODO send midi file instead of file name
        with open(midi_fname, "rb") as f:
            midi_data_str = f.readlines()
        client.send_message("/midi/0", [midi_data_str])

    def get_udp_client(self):
        """
        client allows you to connect and send messages to an OSC server
        """
        client = udp_client.SimpleUDPClient(self.ip, self.port)
        return client


def build_client():
    client = ExampleClient("127.0.0.1", 5005)
    client.generate_messages()


if __name__ == "__main__":
    build_client()
