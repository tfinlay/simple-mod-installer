"""
Curse / CurseForge interface for mod searching

first, we have to GET https://clientupdate-v6.cursecdn.com/feed/addons/432/v10/complete.json.bz2 (a list of all the Curse mods for Minecraft)
second, we need to load them all into CurseMods, losing all unnecessary data.
"""
import threading
import logging
import urllib.request, urllib.error
import bz2
import os
import ijson
from simple_mod_installer import config, util

JSON_URL = "https://clientupdate-v6.cursecdn.com/feed/addons/432/v10/complete.json.bz2"

curse_mods = []
curse_mods_lock = threading.Lock()

logger = logging.getLogger(__name__)


class CurseFile:
    def __init__(self, id, dl_url, filename, game_versions=(), release_type=1):
        self.id = id
        self.download_url = dl_url
        self.filename = filename
        self.release_type = release_type
        self.game_versions = game_versions

        logger.log(1, "Initialising CurseFile: {}".format(self.__repr__()))

    def __repr__(self):
        return '<CurseFile (id: {}, filename: {}, game_versions: {})>'.format(self.id, self.filename, self.game_versions)


class CurseMod:
    def __init__(self, id, name, files=(), authors=()):
        self.name = name
        self.id = id
        self.files = files
        self.authors = authors

    @property
    def mc_versions(self):
        return ((version for version in file.game_versions) for file in self.files)

    def __repr__(self):
        return '<CurseMod (name: {}, id: {})>'.format(self.name, self.id)


# API
def get():
    """
    Executed on startup, creates a new Thread for downloading and parsing the curse mods.
    :return: None
    """
    if config["fetch_curse_moddata"]:
        logging.info("Starting new thread to get curse mods...")
        threading.Thread(target=_get_curse_mods, name="cursemods", daemon=True).start()
    else:
        logging.info("Get curse mods was called, but is not executing as fetch_curse_moddata doesn't resolve to True")


def get_from_id(id):
    """
    search for a mod with id: id
    :param id: int
    :return: CurseMod / None
    """
    with curse_mods_lock:
        for mod in curse_mods:
            if mod.id == id:
                return mod
# /API


def _download_json(dl_loc):
    logger.info("Starting download of moddata JSON")
    try:
        u = urllib.request.urlopen(JSON_URL)
    except urllib.error.URLError as ex:
        logger.error("Failed to download moddata JSON due to URLError: {}. Maybe you're disconnected from the internet?".format(ex))
        raise

    meta = u.info()
    file_size = int(meta["Content-Length"][0])

    logger.debug("File has size: {} bytes".format(file_size))

    file_size_dl = 0
    block_size = 8192  # download in 8MB blocks
    with open(dl_loc, 'wb') as f:
        while True:
            buffer = u.read(block_size)
            if not buffer:
                break  # we've finished the download

            file_size_dl += len(buffer)
            f.write(buffer)

            logger.log(1, "Downloaded {} ({}% complete)".format(file_size_dl, file_size_dl * 100 / file_size))

    logger.info("File download complete!")


def _extract_json(dl_loc, json_loc):
    logger.info("Opening {} for extraction...".format(dl_loc))
    with open(dl_loc, 'rb') as f:
        with open(json_loc, 'wb') as j:
            logger.debug("Opened archive. Attempting to extract data...")
            read = f.read()

            #if not read:
            #    logger.debug("Reading complete, closing file...")
            #    break

            j.write(bz2.decompress(read))

    logger.info("Extraction complete")


def _parse_moddata(json_loc):
    """
    !!DEPRECATED!!
    Load the mod data into CurseMods
    :param json_loc: string
    :return: None
    """
    with open(json_loc, encoding='utf8') as f:
        logger.debug("Opened complete.json successfully.")

        logger.debug("Opening json stream...")
        mods = ijson.items(f, "data.item")

        for mod in mods:
            logger.log(1, "Working with mod id: {}".format(mod["Id"]))
            # parse each mod
            if mod["CategorySection"]["ID"] == 6:
                x = CurseMod(
                    mod["Id"],
                    mod["Name"],
                    files=[
                        CurseFile(
                            file["Id"],
                            file["DownloadURL"],
                            file["FileName"],
                            file["GameVersion"],
                            file["ReleaseType"]
                        )
                        for file in mod["LatestFiles"]],
                    authors=[author["Name"] for author in mod["Authors"]]
                )
                with curse_mods_lock:
                    logger.log(1, "Appending mod to curse_mods...")
                    curse_mods.append(x)


def _get_curse_mods():
    """
    Entrypoint for getting and parsing Curse mods. This should be started in a new thread.
    :return: None
    """
    dl_folder = util.join_path(
        config["application_root"],
        "tmp",
        "cursedata",
    )

    dl_loc = util.join_path(
        dl_folder,
        "cursedata.json.bz2"
    )

    json_loc = util.join_path(
        dl_folder,
        "cursedata.json"
    )

    if not os.path.exists(dl_folder):
        logger.warning("Directory: {} doesn't exist yet, creating...".format(dl_folder))
        os.makedirs(dl_folder)

    logger.info("Getting Curse mods...")
    try:
        _download_json(dl_loc)
    except Exception:
        logger.error("Moddata download failed, maybe the computer is offline. Some Advanced features will be unavailable until reconnection occurs")
        return

    logger.info("Extracting archive...")
    _extract_json(dl_loc, json_loc)

    logger.info("Deleting archive...")
    try:
        os.unlink(dl_loc)
    except Exception as ex:
        logger.error("File Unlink failed with error: {}: {}".format(type(ex).__class__, ex.args))
    else:
        logger.info("Archive deletion complete")

    logger.info("Parsing extracted curse mod data...")
    _parse_moddata(json_loc)
