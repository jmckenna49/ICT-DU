# importing the requests library

import requests

url = "http://localhost:8000/test"
params = { 'address': 'Denver' } 
response = requests.get(url, params)

data = response.text
print("Data: %s\n" % data)

