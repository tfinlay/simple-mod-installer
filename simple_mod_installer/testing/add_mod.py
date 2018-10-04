"""
Uses the web api to add a new Mod
"""
import requests
import webbrowser

x = requests.post("http://localhost:5000/mod/add/download?url=http://localhost:8000/depcheck_testmod.jar")
print(x.content.decode())
#webbrowser.open_new_tab(x.url)
