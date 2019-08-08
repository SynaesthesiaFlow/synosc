import math
from pythonosc import dispatcher
from pythonosc import osc_server

from osc.osc_helper import OscHandler


class OscServer(OscHandler):
    """
    must override: construct_dispatchers()
    https://python-osc.readthedocs.io/en/latest/
    """

    def __init__(self, ip, port):
        OscHandler.__init__(self, ip, port)
        self.ip = ip
        self.port = port
        self.dispatcher = dispatcher.Dispatcher()

    def construct_dispatchers(self):
        # override
        self.dispatcher.map("/filter", print)
        self.dispatcher.map("/volume", self.print_volume_handler, "Volume")
        self.dispatcher.map("/logvolume", self.print_compute_handler, "Log volume", math.log)

    def run(self):
        self.run_server()

    def run_server(self):
        """
        TODO: handle params to start different kinds of servers
        with SynMagEther(gen_muse, qpm, start_time, signals=None, channel=None) as sme:
        """
        server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), self.dispatcher)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()

    def print_volume_handler(self, unused_addr, args, volume):
        print("[{0}] ~ {1}".format(args[0], volume))

    def print_compute_handler(self, unused_addr, args, volume):
        try:
            print("[{0}] ~ {1}".format(args[0], args[1](volume)))
        except ValueError:
            pass


def build_server():
    server = OscServer("127.0.0.1", 5005)
    server.construct_dispatchers().start()


if __name__ == "__main__":
    build_server()
