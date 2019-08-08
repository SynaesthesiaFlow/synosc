from pythonosc import udp_client
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
import random

from osc.osc_helper import OscHandler
from generators.magenta_generator import SynGenModels


class OscClient(OscHandler):
    """
    Class for OSC Clients
    must override: generate_messages()
    https://python-osc.readthedocs.io/en/latest/
    """

    def __init__(self, ip, port):
        OscHandler.__init__(self, ip, port)
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


def build_client():
    client = OscClient("127.0.0.1", 5005)
    client.generate_messages()


if __name__ == "__main__":
    build_client()
