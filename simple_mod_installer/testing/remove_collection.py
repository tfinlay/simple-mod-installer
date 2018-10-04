"""
Uses the web interface to delete a collection
"""
import requests

x = requests.post("http://localhost:5000/collection/remove?id=1")
print(x.content.decode())
