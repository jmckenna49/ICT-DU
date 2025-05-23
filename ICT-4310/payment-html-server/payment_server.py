"""
payment_server.py

A payment HTTP Server for handling only POST requests and sending a basic JSON response
to simulate payment processing.

Author: James McKenna
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import logging
import os.path
import json

# Dummy approved cards and tracking
Approved_Cards = {
    "4111111111111111": "James McKenna",
    "5500000000000004": "Luna McKenna"
}
MAX_LIMIT = 1000
card_totals = {}

class HTTPRequestHandler(SimpleHTTPRequestHandler):
    """ Custom HTTP request handler for POST requests
    """
    def __init__(self, *args, **kwargs):
        # Serve files from the current directory
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def _set_response(self):
        """ Send standard HTTP ok response, 200, with Content-Type set to application/json.
        """
        self.send_response(200)
        self.send_header("Content-Type", "application/json")  # <--- Fixed so this requires json application and content type
        self.end_headers()

    def do_POST(self):
        """ Handles POST requests.
        Expects JSON data with fields: first_name, last_name, credit_card_number,
        expiration_date, ccv, and shipping_address.
        Validates message and returns confirmation or error response.
        """
        # Check to accept only posts to the correct URL Path
        if self.path != "/submit":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return
        else:
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
                    amount = float(received_data.get("amount", "50"))  # <--- Optional amount, default $50

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

                    # Card validation check
                    if credit_card_number not in Approved_Cards:
                        self.send_response(403)  # <--- Forbidden
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "status": "declined",
                            "message": "Card not recognized. Payment rejected."
                        }).encode("utf-8"))
                        return

                    # Check total limit per card
                    current_total = card_totals.get(credit_card_number, 0)
                    if current_total + amount > MAX_LIMIT:
                        self.send_response(402)  # <--- Payment Required
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "status": "declined",
                            "message": f"Card exceeded limit. Current: ${current_total}, attempted: ${amount}"
                        }).encode("utf-8"))
                        return

                    # Update spending record
                    card_totals[credit_card_number] = current_total + amount

                    # simulate successful payment processing
                    payment_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "credit_card_number": credit_card_number,
                        "expiration_date": expiration_date,
                        "ccv": ccv,
                        "shipping_address": shipping_address,
                        "amount": amount
                    }

                    # save to a file (e.g., payments.json)
                    try:
                        if os.path.exists("payments.json"):
                            with open("payments.json", "r+", encoding="utf-8") as f:
                                existing = json.load(f)
                                existing.append(payment_data)
                                f.seek(0)
                                json.dump(existing, f, indent=4)
                        else:
                            with open("payments.json", "w", encoding="utf-8") as f:
                                json.dump([payment_data], f, indent=4)

                    except Exception as file_error:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        error_response = {"error": f"Failed to write to file: {file_error}"}
                        self.wfile.write(json.dumps(error_response).encode("utf-8"))
                        return

                    # respond to client
                    payment_response = {
                        "message": f"Payment of ${amount} submitted for {first_name} {last_name}.",
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
        print("\nShutting down server...")
        httpd.server_close()
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
        