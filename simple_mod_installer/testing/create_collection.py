"""
Uses the web api to create a new Collection
"""
import requests
import webbrowser

x = requests.post("http://localhost:5000/collection/add?name=Best Mods 2017&mcversion=1.7.10&version-id=1.7.10")
print(x.content.decode())
#webbrowser.open_new_tab(x.url)
