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
    def do_GET(self):
        """ Handle GET requests, if file exists serve it.
        Otherwise log the request.
        """
        request = urllib.parse.urlparse(self.path)
        file = self.directory + request.path
        
        if os.path.exists(file):
            super().do_GET()
        else:
            logging.info("GET request, \nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
            logging.info("File %s not found.", file)
            self._set_response()
            self.wfile.write(f"GET request for {self.path}".encode('utf-8'))

    def do_POST(self):
        """ Handles POST requests.
        Expects JSON data with fields: first_name, last_name, credit_card_number,
        expiration_date, ccv, and shipping_address.
        Validates message and returns confirmation or error response.
        """

        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    str(self.path), str(self.headers), post_data.decode('utf-8'))
        
        content_type = self.headers.get('Content-Type', '')
        
        try:
            # check if the header is json
            if "application/json" in content_type:
                # parse the incoming JSON
                received_data = json.loads(post_data)

                # get all required fields
                first_name = received_data.get("first_name")
                last_name = received_data.get("last_name")
                credit_card_number = received_data.get("credit_card_number")
                expiration_date = received_data.get("expiration_date")
                ccv = received_data.get("ccv")
                shipping_address = received_data.get("shipping_address")

                # if any field is missing or empty, return 400 Bad Request
                if not all([first_name, last_name, credit_card_number, expiration_date, ccv, shipping_address]):
                    self.send_response(400)  # <--- Bad Request
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    error_response = {
                        "error": "Missing one or more required fields: first_name, last_name, credit_card_number, expiration_date, ccv, shipping_address"
                    }
                    self.wfile.write(json.dumps(error_response).encode("utf-8"))
                    return

                # simulate successful payment processing
                payment_response = {
                    "message": f"Payment submitted for {first_name} {last_name}.",
                    "status": "approved"
                }
                self._set_response()
                self.wfile.write(json.dumps(payment_response).encode('utf-8'))
                return

            # if data isn't JSON
            else:
                self.send_response(415)  # <--- Unsupported Media Type
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                error_response = {"error": "Unsupported type, only application/json applicable"}
                self.wfile.write(json.dumps(error_response).encode("utf-8"))

        # catch-all for parsing or other errors
        except Exception as e:
            self.send_response(400)  # <--- Bad Request
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