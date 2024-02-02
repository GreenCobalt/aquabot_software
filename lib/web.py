from flask import Flask, Response

class EndpointAction(object):
    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        return self.action()
        
class FlaskAppWrapper(object):
    app = None
    def __init__(self, name, host, port):
        self.host = host
        self.port = port
        
        self.app = Flask(name)

    def run(self):
        self.app.run(debug=False, use_reloader=False, host=self.host, port=self.port)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))

class WEB():
    def __init__(self, DEBUG, host, port):
        self.app = FlaskAppWrapper(__name__, host, port)
        self.app.add_endpoint(endpoint='/api', endpoint_name='api', handler=self.api)
        self.controller_values = [ [ 128, 128 ], [ 128, 128 ] ]
        
    def run(self):
        self.app.run()
        
    def getControllerValues(self):
        return self.controller_values
        
    def api(self):
        return Response(response="fdsfdsf", status=200, headers={})
