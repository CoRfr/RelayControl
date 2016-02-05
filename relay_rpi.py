
import RPi.GPIO as GPIO
from relay import Relay

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class RelayRpi(Relay):
    def __init__(self, id, gpio):
        self.id = id
        self.gpio = gpio

        GPIO.setup(self.gpio, GPIO.OUT)

    def get_state(self):
        return GPIO.input(gpio)

    def set_state(self, state):
        if state == "true":
            state = True
        else:
            state = False

        GPIO.output(gpio, state)
