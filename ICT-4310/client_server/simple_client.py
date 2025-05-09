"""
simple_client.py

A simple HTTP Server for handling only POST requests and sending a basic JSON response
to simulate payment processing.

Author: James McKenna
"""
import requests

class SimpleHttpClient:
    """Simple HTTP Client to send JSON data to a server via POST request
    """
    def __init__(self, host='localhost', port=8000):
        """Initialize the client with server host and port

        Args:
            host (str, optional): Server hostname or IP Address. Defaults to 'localhost'.
            port (int, optional): Server port number. Defaults to 8000.
        """
        self.base_url=f"http://{host}:{port}"

    def send_json(self, path, data):
        """Send a Post request with JSON data to path
        Args:
            path (str): Endpoint path on the server, /process
            data (dict): Dictionary that will be sent as json

        Returns:
           tuple: HTTP status code and parsed JSON response.
        """
        # Send POST Request
        url = self.base_url + path
        headers = {
            'Content-Type': 'application/json'
        }
        # Automatically handles the json data with the json parameter for requests.post(json=)
        response = requests.post(url, headers=headers, json=data)
        return response.status_code, response.json()

if __name__ == "__main__":
    client = SimpleHttpClient()

    #Example payment data to send
    json_data = {
        "payer": "James",
        "payee": "Dutch Bros",
        "amount": 10.99
    }

    json_data2 = {
        "user": "Joe",
        "location": "DU",
        "time": 1300
    }
    status, response = client.send_json('/process', json_data)
    print("\nSent JSON Data:")
    print("Status", status)
    print("Response from server:\n", response)

    status, response = client.send_json('/process', json_data2)
    print("\nSent JSON Data:")
    print("Status", status)
    print("Response from server:\n", response)
