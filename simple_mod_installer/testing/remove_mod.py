"""
Uses the web api to add a new Mod
"""
import requests
import webbrowser

x = requests.post("http://localhost:5000/mod/remove?id=1")
print(x.content.decode())
#webbrowser.open_new_tab(x.url)
