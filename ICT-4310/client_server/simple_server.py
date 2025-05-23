"""
simple_server.py

A simple HTTP Server for handling only POST requests and sending a basic JSON response
to simulate payment processing.

Author: James McKenna
"""
from http.server import SimpleHTTPRequestHandler, HTTPServer
import logging
import urllib.parse
import os.path
import json

class HTTPRequestHandler(SimpleHTTPRequestHandler):
    """ Custom HTTP request handler for POST requests
    """
    def _set_response(self):
        """ Send standard HTTP ok response, 200, with Content-Type set to application/json.
        """
        self.send_response(200)
        self.send_header("Content-Type", "application/json") # <--- Fixed so this requires json application and content type
        self.end_headers()

    def do_POST(self):
        """ Handles POST requests.
        Expects JSON data with "payer", "payee", and "amount" fields.
        Validates message and returns confirmation or error response.
        """

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        content_type = self.headers.get('Content-Type', )
        # Parse the incoming JSON
        try:
            # check if the header is json
            if "application/json" in content_type:
                # if it is check the data for payer, payee, and amount information
                received_data = json.loads(post_data)
                payer = received_data.get("payer")
                payee = received_data.get("payee")
                amount = received_data.get("amount")
                # if the data is not correct error
                if not (payer and payee and amount):
                    self.send_response(400) # <--- Bad Request
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    error_response = {"error": "Missing payment fields (payer, payee, amount)"}
                    self.wfile.write(json.dumps(error_response).encode("utf-8"))
                    return
                # if payment is received correctly set up a response message to send to the client
                payment_response = {
                    "message":f"Payment of ${amount} from {payer} to {payee} has been received.",
                    "status": "approved"
                }
                self._set_response()
                self.wfile.write(json.dumps(payment_response).encode('utf-8'))
                return
            # if data isn't json
            else:
                self.send_response(415)  # <--- Not supported type, only json
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                error_response = {"error": "Unsupported type, only json applicable"}
                self.wfile.write(json.dumps(error_response).encode("utf-8"))
        # if parsing the response didn't work, or the data isn't json
        except Exception as e:
            self.send_response(400) # <--- Bad Request
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode("utf-8"))

def run(server_class=HTTPServer, handler_class=HTTPRequestHandler, port=8000):
    """
    Initialize and run the HTTPServer.

    HTTPServer is a builtin Python class that contains the basics necessary to implement
    an HTTP server. In order to use it you create an instance of the server, tell it
    what port to listen on and give it a RequestHandler class to actually process requests.
    This is typically a subclass of BaseHTTPRequestHandler. In order to use it you must
    override at least one of do_GET or do_POST.

    Args:
      server_class: the name of the server class to instantiate for the web server.
      handler_class: the name of the class to use for the RequestHandler.
      port: the port to listen on, must be greater than 1024.
    """
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
