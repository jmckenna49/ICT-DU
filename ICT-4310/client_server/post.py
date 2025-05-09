import requests
import urllib.parse

url = 'http://localhost:8000/'
myobj = {'somekey': 'somevalue'}

r = requests.post(url, data = myobj)
v = urllib.parse.parse_qsl(r.text)
print(r.text)
print(v)

