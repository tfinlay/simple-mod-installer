import os
import logging
import subprocess
import platform
import sys
from functools import wraps
from urllib.request import quote
from flask import request, redirect, url_for

logger = logging.getLogger(__name__)


def confirmation_required(data_fn):
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.args.get('confirm') != '1':
                data = data_fn()
                title = data["title"]
                desc = data["desc"]
                return redirect(url_for(
                    'confirm',
                    title=title,
                    desc=desc,
                    action_url=quote(request.url)
                ))
            return f(*args, **kwargs)
        return wrapper
    return inner


def join_path(*args):
    """
    Generates a correct path for any platform
    :param args:
    :return: string
    """
    return os.path.join(*args)


def get_default_tfff1_loc():
    """
    Gets the default location of /Tfff1 directory for this system
    :return: string, absolute path.
    """
    if platform.system() == 'Windows':  # Windows
        return join_path(os.getenv('APPDATA'), "Tfff1")
    else:  # *nix
        return join_path(os.getenv('HOME'), "Tfff1")


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
    return not os.path.exists(join_path(containing_folder, filename))


def find_unique_name(containing_folder, filename, max_add_size=999):
    """
    Finds a version of filename which isn't taken in the containing_folder
    :param containing_folder: string, absolute path to the target folder
    :param filename: string, filename of the file
    :param max_add_size: int, the maximum integer size to be added to the end of the file
    :return: string, new and unique file name
    """
    filename_no_ext, filename_ext = os.path.splitext(filename)

    logger.info("Finding a unique name for the file: {} in directory: {}".format(filename, containing_folder))

    for i in range(max_add_size):
        if is_unique_filename(
                containing_folder,
                "{}_{}{}".format(
                    filename_no_ext,
                    i,
                    filename_ext
                )
        ):
            logger.info("Found unique name: {}_{}{}".format(filename_no_ext, i, filename_ext))
            return "{}_{}{}".format(
                            filename_no_ext,
                            i,
                            filename_ext
                        )

    logger.error("Maximum Add Size has been exceeded!")
    raise ValueError("Max Add Size has been exceeded!")


def get_parent_dir(path):
    """
    Gets the parent directory of the end of path
    :param path: string, absolute path
    :return: string, absolute path, but up a level
    """
    return os.path.dirname(path)


def create_symbolic_link(file, target):
    """
    Creates a symbolic link
    :param file: string, absolute path to the file which we're to create a sym link to
    :param target: string, absolute path to where the sym link will be placed
    :return: None
    """
    try:
        os.symlink(file, target)
    except NotImplementedError:
        logger.critical("Symbolic links not supported on this platform")
        raise
    except OSError:
        logger.critical("Not sufficient permissions")
        raise


def restart_with_root():
    """
    Restarts the application as root
    """
    if platform.system() == 'Windows':
        os.execv('cmd', join_path(os.path.pardir(os.path.pardir(__file__)), 'start_root.cmd'))
    else:
        os.execv(sys.executable, ['sudo python'] + sys.argv)


def resolve_url_bool(val):
    """
    Resolves the value of a URL as to whether it's True or False
    :param val: string
    :return: bool
    """
    if isinstance(val, str):
        if val.lower() == "true" or val == "1":
            return True
        else:
            return False
    else:
        return False


def open_file_browser(path):
    """
    Opens ex explorer.exe, nautilus at path
    from: https://stackoverflow.com/questions/1795111/is-there-a-cross-platform-way-to-open-a-file-browser-in-python
    :param path: string, absolute path
    :return: None
    """
    if sys.platform == 'win32':
        #subprocess.Popen(['start', path], shell=True)
        os.startfile(path)

    elif sys.platform == 'darwin':
        subprocess.Popen(['open', path])

    else:
        try:
            subprocess.Popen(['xdg-open', path])
        except OSError:
            logger.error("Presumably *nix system xdg-open failed for path: {}".format(path))