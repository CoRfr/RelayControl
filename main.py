#!/usr/bin/env python2

from flask import Flask, request
import json
import os
import socket
from pprint import pprint
from optparse import OptionParser

app = Flask("relayControl")
relays = {}

def load_relays(cfg_file):
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

from optparse import OptionParser

parser = OptionParser()
parser.add_option('-H', "--host", dest="host", metavar="HOST",
                  default="0.0.0.0",
                  help="the hostname to listen on. Set this to '0.0.0.0' to have the server available externally as well.")
parser.add_option('-p', "--port", dest="port", type="int", metavar="PORT",
                  default=8080,
                  help="the port to listen on.")
parser.add_option('-c', "--cfg", dest="cfg_file", metavar="FILE",
                  default="settings/default.json",
                  help="config file in JSON format.")
parser.add_option('-d', "--debug", dest="debug",
                  default=False,
                  help="debug mode")

if __name__ == "__main__":
    (options, args) = parser.parse_args()

    load_relays(options.cfg_file)

    app.run(host=options.host, port=options.port, debug=options.debug)
