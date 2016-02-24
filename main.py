#!/usr/bin/env python2

from flask import Flask, request, url_for, escape
import json
import os
import socket
from pprint import pprint
from optparse import OptionParser

app = Flask(__name__)
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

def list_routes():
    import urllib
    output = []
    routes = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "_%s_" % arg

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        route = {
            "url": url,
            "methods": methods,
            "endpoint": rule.endpoint
        }
        routes.append(route)

    return routes

@app.route('/')
def help():
    output = "<html><body><h1>RelayControl</h1><br/><table>"
    for route in list_routes():
        output += "<tr><td><pre>%s</pre></td><td>%s</td><td>%s</td></tr>" % (escape(route["url"]), route["methods"], route["endpoint"])
    output += "</table></body></html>"
    return output

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
    next_state = False

    if 'state' in request.form:
        next_state = request.form['state']
    elif 'Content-Type' in request.headers:
        if request.headers['Content-Type'] == 'application/json':
             data = json.loads(request.data)
             if not 'state' in data.keys():
                 raise("Invalid JSON request")
             next_state = data['state']
        else:
             raise Exception("Unknown content type")
    else:
        raise Exception("Invalid request")

    relay.set_state(next_state)

    return json.dumps(relay.to_hash())

@app.route('/relays/<relay_id>/toggle')
def toggle_relay(relay_id):
    if not relay_id in relays:
        return ""

    relay = relays[relay_id]

    relay.toggle_state()

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
                  help="config file in JSON format.")
parser.add_option('-d', "--debug", dest="debug", action="store_true",
                  default=False,
                  help="debug mode")

if __name__ == "__main__":
    (options, args) = parser.parse_args()

    cfg_file = options.cfg_file
    if not cfg_file:
        cfg_file = os.path.join( os.path.dirname( os.path.realpath(__file__) ), "settings/default.json")

    load_relays(cfg_file)

    app.run(host=options.host, port=options.port, debug=options.debug)
