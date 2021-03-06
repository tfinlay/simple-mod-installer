"""
HTTP Actions
"""
import os
import json
import codecs
import urllib.request
from simple_mod_installer.util import get_parent_dir
from urllib.request import urlopen, quote
import logging

logger = logging.getLogger(__name__)


def download_to_file(url, location):
    """
    does method on a url and saves the result
    :param url: string
    :param location: string, absolute path to where the data should be saved
    :return: None
    """
    loc_parent = get_parent_dir(location)
    logger.info("Creating {} if required".format(loc_parent))
    # Check if the directory to contain the file exists:
    os.makedirs(loc_parent, exist_ok=True)

    protocol, url = url.split("://", 1)

    # Escape the URL
    logger.debug("Escaping URL: `{}`".format(url))
    url = quote(url)

    # Open the URL
    logger.info("Opening URL: `{}://{}`".format(protocol, url))
    f = urlopen("{}://{}".format(protocol, url))

    with open(location, 'wb') as local_file:
        local_file.write(f.read())

    logger.info("Download successful")


def load_json_from_response(response, encoding="utf-8"):
    """
    reads JSON from a urllib.request.urlopen() return
    :param url: string
    :return: dict or list, encoded JSON
    """
    reader = codecs.getreader(encoding)
    return json.load(reader(response))
