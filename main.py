#!/usr/bin/env python2

from flask import Flask, request
import json
import os
import socket
from pprint import pprint

app = Flask("relayControl")
relays = {}

def load_relays(cfg_file=None):
    if not cfg_file:
        hostname = socket.gethostname()
        cfg_file = "settings/%s.json" % hostname
        if not os.path.isfile(cfg_file):
            cfg_file = "settings/default.json"

    cfg_data = open(cfg_file).read()
    data = json.loads(cfg_data)

    default_type = 'rpi'
    if data["default_type"]:
        default_type = data["default_type"]

    current_id = 0
    for info in data["relays"]:

        # Allocate ID
        relay_id = current_id
        if "id" in info:
            relay_id = info["id"]
        else:
            current_id += 1

        relay_id = "%d" % relay_id

        relay_type = default_type
        if "type" in info:
            relay_type = info["type"]

        relay = None
        if relay_type == "rpi":
            from relay_rpi import RelayRpi
            gpio = info["gpio"]
            relay = RelayRpi(relay_id, int(gpio))
        elif relay_type == "test":
            from relay_test import RelayTest
            gpio = info["gpio"]
            relay = RelayTest(relay_id, int(gpio))            
        else:
            raise Exception("Unknown relay type %s" % relay_type)

        relays[relay_id] = relay

    return

@app.route('/')
def help():
    return "RelayControl"

@app.route('/relays')
def list_relays():
    relays_data = []
    for info in relays:
        relay = relays[info]
        relays_data.append(relay.to_hash())
    return json.dumps(relays_data)

@app.route('/relays/<relay_id>', methods=['GET'])
def get_relay(relay_id):
    if not relay_id in relays:
        return ""
    relay = relays[relay_id]
    return json.dumps(relay.to_hash())

@app.route('/relays/<relay_id>', methods=['POST'])
def set_relay(relay_id):
    if not relay_id in relays:
        return ""

    relay = relays[relay_id]

    if not request.form['state']:
        return "Invalid Request"

    relay.set_state(request.form['state'])

    return json.dumps(relay.to_hash())

if __name__ == "__main__":
    load_relays()
    app.run()
