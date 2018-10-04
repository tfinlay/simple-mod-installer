"""
Uses the web api to remove a mod from a collection
"""
import requests
import webbrowser

x = requests.post("http://localhost:5000/collection/1/rem_mod?id=1")
print(x.content.decode())
#webbrowser.open_new_tab(x.url)
