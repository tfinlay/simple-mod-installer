"""
Entrypoint for the application. It has two key roles:
1. Checking for and installing updates
2. Making sure the process is elevated (running as admin / anything with symlink permissions)
"""
import platform
import subprocess
import urllib.request
import json


UPDATE_INFO_URL = "https://simplemodinstallerupdatehost.herokuapp.com/currentversion.json"


def run_as_admin(path_to_executable):
    """
    Spawns executable as admin on windows, or as root on *nix
    :param path_to_executable: string, absolute path to the executable
    :return: None
    """
    if platform.system() == "Windows":
        subprocess.call(["popen", path_to_executable])


def is_less(current_version, latest_version):
    current, latest = current_version.split("."), latest_version.split(".")

    for currentX, latestX in zip(current, latest):
        if currentX < latestX:
            return True

    return False


def check_for_updates():
    with urllib.request.urlopen(UPDATE_INFO_URL) as res:
        latest_version = json.load(res)

    with open("releaseinfo.json", 'r') as f:
        current_version = f.read()

    print(latest_version)

    if is_less(current_version, list(latest_version.keys())[0]):
        # we need to update
        print("Update required!")


if __name__ == "__main__":
    check_for_updates()
    run_as_admin("npp")
else:
    print("WARNING: This module shouldn't ever be imported")