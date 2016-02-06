
from relay import Relay

class RelayTest(Relay):
    def __init__(self, id, gpio):
        self.id = id
        self.gpio = gpio
        self.state = True

    def get_state(self):
        return self.state

    def set_state(self, state):
        if state == True or state == "true":
            self.state = True
        else:
            self.state = False
