import os.path
import platform
import json
import zipfile


def join_path(*args):
    """
    Generates a correct path for any platform
    :param args:
    :return: string
    """
    return os.path.join(*args)


def get_default_mc_loc():
    """
    Gets the default location of Minecraft for this system
    :return: string
    """
    if platform.system() == 'Windows':  # Windows
        return join_path(os.getenv('APPDATA'), '.minecraft')  # C:\Users\<user name>\AppData\Roaming
    elif platform.system() == 'Darwin':  # MacOS
        return join_path(os.getenv('HOME'), 'Library', 'Application Support', 'minecraft')  # /home/<user name>/Library/Application Support/minecraft
    else:  # Linux
        return join_path(os.getenv('HOME'), '.minecraft')  # /home/<user name>/.minecraft


def attempt_load_mcmodinfo(filepath):
    """
    Returns the mcmod.info file's contents (as dictionary) if available
    :param filepath: string, absolute path to the mod file
    :return: dict
    """
    try:
        with zipfile.ZipFile(filepath, 'r') as modfile:
            with modfile.open('mcmod.info') as info:
                print(json.load(info))
                return json.load(info)
    except Exception:
        return None


def open_browser(url):
    """
    Opens URL in the default browser
    :param url: string
    :return: None
    """
    import webbrowser
    webbrowser.open_new(url)


def verify_name(name):
    """
    Verifies that a name is valid
    :param name: string
    :return: bool
    """
    if name and not name.isspace():  # if it's not empty/NULL and it's not whitespace
        return True
    else:
        return False


def get_file_name(path):
    """
    Returns the file name, derived from the path
    :param path: string
    :return: string
    """
    return os.path.basename(path)


def is_unique_filename(containing_folder, filename):
    """
    Checks if a filename is unique in containing_folder
    :param containing_folder: string, absolute path to the target folder
    :param filename: string, filename of the file
    :return: bool
    """
    return os.path.exists(join_path(containing_folder, filename))


def find_unique_name(containing_folder, filename, max_add_size=999):
    """
    Finds a version of filename which isn't taken in the containing_folder
    :param containing_folder: string, absolute path to the target folder
    :param filename: string, filename of the file
    :param max_add_len: int, the maximum integer size to be added to the end of the file
    :return: string, new and unique file name
    """
    filename_no_ext, filename_ext = os.path.splitext(filename)

    for i in range(max_add_size):
        if is_unique_filename(
                containing_folder,
                "{}{}{}".format(
                    filename_no_ext,
                    i,
                    filename_ext
                )
        ):
            return "{}{}{}".format(
                            filename_no_ext,
                            i,
                            filename_ext
                        )
