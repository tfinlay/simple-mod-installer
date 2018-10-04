"""
Uses the web api to add a mod to a collection
"""
import requests
import webbrowser

x = requests.post("http://localhost:5000/collection/1/add_mod?id=2")
print(x.content.decode())
#webbrowser.open_new_tab(x.url)
