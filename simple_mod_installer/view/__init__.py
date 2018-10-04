import time
import logging
import urllib.request
import webview


logger = logging.getLogger(__name__)

def block_until_server_started(url):
    """
    pings the server until it's started up (blocking)
    :return: None
    """
    while True:
        res = urllib.request.urlopen(url)
        if res.getcode() == 200:
            break
        time.sleep(0.5)


def run_view(url, stop_event):
    """
    this should be in it's own thread
    :param url:string
    :param stop_event: threading.Event, triggered when shutdown time happens
    :return: None
    """
    logger.info("waiting for webserver to start...")
    block_until_server_started(url)

    logger.info("starting view...")

    webview.create_window(
        title="Simple Mod Installer",
        url=url
    )

    # the window has been closed, lets shut down
    logger.info("View closed, shutting down...")
    webview.destroy_window()

    stop_event.set()

