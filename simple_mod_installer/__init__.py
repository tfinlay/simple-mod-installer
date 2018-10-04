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
import sys
import os

# init config. This variable is referenced everywhere throughout the application
path_to_lib = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, path_to_lib)


from simple_mod_installer.conf import Config

config = Config()


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
    from simple_mod_installer import webserver

    webserver = threading.Thread(target=webserver.start_server).start()  # open the Flask webserver in a seperate thread so that other tasks may continue in the background.
    logger.info("Web server started successfully")

    logger.info("Getting curse mods...")
    from simple_mod_installer.searchmods import cursemods
    cursemods.get()

    logger.info("Startup Successful!")


if __name__ == '__main__':
    main()
