"""
Uses the web api to check the dependencies of a mod
"""
import requests
import webbrowser

x = requests.post("http://localhost:5000/collection/1/dep_check")
print(x.content.decode())
#webbrowser.open_new_tab(x.url)
