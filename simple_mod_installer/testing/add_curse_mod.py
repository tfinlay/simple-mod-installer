"""
Uses the web api to add a new Mod
"""
import requests
import webbrowser

x = requests.post("http://localhost:5000/mod/add/curse?curse_id=241018&file_id=2324085&url=https://addons.cursecdn.com/files/2324/85/examplemod-1.8.5-1.0 (2).jar")
print(x.content.decode())
#webbrowser.open_new_tab(x.url)
