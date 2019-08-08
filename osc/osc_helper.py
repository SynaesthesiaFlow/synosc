"""
utility functions for OSC

MIDI is passed within OSC: http://opensoundcontrol.org/wrapping-other-protocols-inside-osc
  - python_osc docs: https://python-osc.readthedocs.io/en/latest/dispatcher.html
  - OSC spec: http://opensoundcontrol.org/spec-1_0
  - intro to osc: https://www.linuxjournal.com/content/introduction-osc
Notes
  - OSC Address Space: list of all the messages a server understands
  - OSC Schema: OSC Address Space plus the semantics of all the messages
      - Expected argument type(s) for each message
      - Units and allowable ranges for each parameter
      - The effect of each message (with respect to some model of the behavior of the OSC server as a whole)
      - If and how the effects of multiple messages interact

"""
import threading


class OscHandler(threading.Thread):

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        super(OscHandler, self).__init__()

    def run(self):
        pass
