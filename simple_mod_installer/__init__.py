"""
The entrypoint of the application

Notes:
    Made with Python v3.6.1.
    Backwards compatibility may exist, but Python's lower than 3.6.1 are not targeted and therefore not ensured to work.
    Any Backwards compatibility which may exist below Python 3.6.1 is subject to change without prior notice.
"""
import logging, logging.config
import logging.handlers
import threading
import pathlib
import time
import sys
import os

# init config. This variable is referenced everywhere throughout the application
path_to_lib = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, path_to_lib)


from simple_mod_installer.conf import get_config

config = get_config() #Config()

'''
class c:
    def __init__(self):
        self.conf = Config()
        self.conf_lock = threading.Lock()

    def __getitem__(self, item):
        try:
            self.conf_lock.acquire()
        finally:
            return self.conf[item]

    def __setitem__(self, key, value):
        try:
            self.conf_lock.acquire()
        finally:
            self.conf[key] = value
            self.conf_lock.release()
'''


def main():
    import sys
    try:
        logging.config.dictConfig(config["logging"])

        logger = logging.getLogger()

        logger.info("Logger initialised")
    except Exception as ex:
        print("[ERROR]: Unable to start: Logging failed: {}: \n{}".format(ex.__class__.__name__, ex.args))
        sys.exit(1)

    logger.info("Starting...")

    import pprint
    logger.debug("Sys path: `\n{}\n`".format(sys.path))

    logger.info("Loaded Config with application data root at: {} and Minecraft Directory at: {}".format(config["application_root"], config["minecraft_directory"]))

    if not os.path.exists(config["application_root"]):
        logger.warning("Application root doesn't exist. Creating...")
        os.makedirs(config["application_root"])

    # GET GOING!
    if not pathlib.Path(os.path.join(config["application_root"], "moddata.sqlite")).is_file():  # if the database doesn't exist yet, then create it
        logger.warning("Database file does not exist. Creating...")

        from simple_mod_installer.database import init_db

        init_db()
        logger.info("Database created successfully")

    logger.info("Starting web server...")

    # get started:
    from simple_mod_installer import webserver, view

    stop_event = threading.Event()

    webserver = threading.Thread(target=webserver.start_server, daemon=True, name="webserver").start()  # open the Flask webserver in a seperate thread so that other tasks may continue in the background.
    logger.info("Web server started successfully")

    webserver_url = "http://127.0.0.1:{}".format(config["webserver_port"])

    logger.info("Waiting to start webview...")
    webview_thread = threading.Thread(target=view.run_view, args=(webserver_url,stop_event), daemon=True, name="webview")#threading.Thread(target=ping_until_server_started, args=(webserver_url, start_webview, (webserver_url,))).start()
    #webview_thread.start()

    logger.info("Getting curse mods...")
    from simple_mod_installer.searchmods import cursemods
    cursemods.get()

    logger.info("Startup Successful!")
    '''
    import webview
    webview.evaluate_js('window.location.reload(true);')
    webview.evaluate_js(r"window.onerror = function(msg, url, linenumber) {alert('Error message: '+msg+'\nURL: '+url+'\nLine Number: '+linenumber);return true;}")
    with open("static/dist/inline.bundle.js") as f:
        webview.evaluate_js(f.read())
    with open("static/dist/polyfills.bundle.js") as f:
        webview.evaluate_js(f.read())
    with open("static/dist/styles.bundle.js") as f:
        webview.evaluate_js(f.read())
    with open("static/dist/vendor.bundle.js") as f:
        webview.evaluate_js(f.read())
    with open("static/dist/main.bundle.js") as f:
        webview.evaluate_js(f.read())
    '''


    while not stop_event.is_set():
        time.sleep(0.5)

    logger.info("Main thread closed")


if __name__ == '__main__':
    main()
