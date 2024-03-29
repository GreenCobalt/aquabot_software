import json
import logging
import time
from websocket_server import WebsocketServer


class WEB():
    def __init__(self, DEBUG, host, port):
        self.controller_values = json.loads(
            '{"axes":{"axis_l":[0,0],"axis_r":[0,0],"trigger_l":0,"trigger_r":0},"buttons":{"button_a":false,"button_b":false,"button_x":false,"button_y":false,"button_trigger_l":false,"button_trigger_r":false,"button_select":false,"button_start":false,"button_thumb_l":false,"button_thumb_r":false}}')

        self.server = WebsocketServer(
            host=host, port=port, loglevel=logging.INFO)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)

    def new_client(self, client, server):
        server.send_message(client, "HLO")
        print("new client")
    
    def message_received(self, client, server, message):
        msg = json.loads(message)
        if msg["type"] == "ACQ":
            print("connection established")
            server.send_message(client, "REQ")
        elif msg["type"] == "DAT":
            self.controller_values = msg["data"]
            time.sleep(0.05)
            server.send_message(client, "REQ")

    def run(self):
        self.server.run_forever()

    def getControllerValues(self):
        return self.controller_values
