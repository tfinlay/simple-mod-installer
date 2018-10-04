"""
Everything to do with Mods
"""
import logging
from pprint import pformat
import os
import zipfile
import json
from jsoncomment import JsonComment
import shutil
import simple_mod_installer.searchmods.cursemods
from simple_mod_installer import config
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from simple_mod_installer.database import db_session
from simple_mod_installer.database.models import Mod, DepMod, ModAuthor
from simple_mod_installer import exceptions
from simple_mod_installer.util import join_path, get_file_name, find_unique_name, get_parent_dir
ALLOWED_EXTENSIONS = frozenset(['jar', 'zip'])

#logging.config.dictConfig(config["logging"])
logger = logging.getLogger(__name__)


def attempt_load_mcmodinfo(filepath):
    """
    Returns the mcmod.info file's contents (as dictionary) if available
    :param filepath: string, absolute path to the mod file
    :return: dict
    """
    logger.info("Attempting to load MCMod.info from {}".format(filepath))
    parser = JsonComment(json)

    try:
        with zipfile.ZipFile(filepath, 'r') as modfile:
            try:
                with modfile.open('mcmod.info') as info:
                    #print(info.read().decode('utf-8'))
                    #i = json.loads(info.read().decode('utf-8').replace("\n", ""))
                    try:
                        logger.debug("Attempting to parse MCMod.info...")
                        i = parser.loads(info.read().decode('utf-8'), strict=False)
                    except UnicodeDecodeError:
                        logger.warning("Decoding failed, skipping")
                        i = None

                    logger.debug("MCModInfo data parsed to be:\n```\n{}\n```".format(pformat(i)))
                    logger.info("Successfully loaded mod info: {}".format(i))
                    return i
            except KeyError as e:
                logger.error("Failed to load MCMod.info from {} as it's not present in the archive.".format(filepath))
    except Exception as ex:
        logger.error("Failed to load MCMod.info from {} due to {} ({})".format(filepath, type(ex).__name__, ex.args))
        #return None
        raise


def allowed_modfile(filename):
    """
    determines whether or not this modfile type is allowed
    :param filename: string
    :return: bool
    """
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS  # it it's extension is allowed


class MCMod:
    def __init__(self, modid=None, name=None, version=None, mcversion=None, update_url=None, required_mods=(), description=None, creds=None):
        self.logger = logging.getLogger(__name__ + '.McMod')

        self.modid = modid
        self.name = name
        self.version = version
        self.mc_version = mcversion
        self.update_url = update_url
        self.description = description
        self.credits = creds
        self.dependencies = []
        self.authors = []

        self.logger.debug("MCMod Initialised: {}".format(self))

    def add_to_database(self, filename, dl_url=None, curse_id=None, curse_file_id=None):
        """
        Add this mod to the database
        :param filename: string, absolute path to the filename
        :param dl_url: string, URL the mod was downloaded from, if it was acquired via direct DL
        :return: None
        """
        self.logger.debug("Adding self to database...")
        # init the mod
        m = Mod(
            filename,
            self.name,
            self.modid,
            self.version,
            self.mc_version,
            self.update_url,
            self.description,
            self.credits,
            dl_url,
            self.dependencies,
            curse_id=curse_id,
            curse_file_id=curse_file_id,
            authors=self.authors
        )

        # add the Mod to the database
        db_session.add(m)
        self.logger.debug("Added to database successfully")

    def __repr__(self):
        return '<MCMod modid: {}, name: {}>'.format(self.modid, self.name)


class MCModFile:
    """
    Based on the specification: https://mcforge.readthedocs.io/en/latest/gettingstarted/structuring/#the-mcmodinfo-file
    """
    def __init__(self, mcmod_info=None):
        self.logger = logging.getLogger(__name__ + ".MCModFile")
        self.raw_data = mcmod_info
        self.mods = [MCMod()]

        self.logger.debug("MCModFile Initialised!")

    def add_to_database(self, filename, dl_url=None, curse_id=None, curse_file_id=None):
        """
        Add each mod to the database
        :param filename: string, absolute path to the filename
        :param dl_url: string, URL the mod was downloaded from, if it was acquired via direct DL
        :return: None
        """
        self.logger.debug("Adding mods to database...")
        for mod in self.mods:
            mod.add_to_database(filename, dl_url, curse_id=None, curse_file_id=None)

        # commit all of the changes
        db_session.commit()

        self.logger.debug("Mod Commit successful")

    def populate(self):
        self.logger.debug("Populating mods...")
        # populate a list of mods:
        try:
            self.logger.debug("Attempting to read as Mod List Version 2...")
            if self.raw_data["modListVersion"] == 2:  # v2 has mods nested under modList
                self.logger.debug("Is version 2. Populating...")
                self._populate_mods(self.raw_data["modList"])
            else:  # in v1, mods are top level
                self.logger.debug("Is version 1. Populating...")
                self._populate_mods(self.raw_data)
        except (KeyError, TypeError):  # Executing the above code on a v1 mcmod.info may cause an error. This identifies it:
            self.logger.debug("Caught KeyError or TypeError. Is version 1. Populating...")
            self._populate_mods(self.raw_data)

        self.logger.debug("Populating Complete. self.mods is: {}".format(self.mods))

    def _populate_mods(self, modlist):
        try:
            self.logger.debug("Attempting to populate mods...")
            for mod in modlist:
                self.logger.debug("Working with mod: {}".format(mod))
                m = MCMod()
                try:
                    self.logger.debug("Trying to get name...")
                    m.name = mod["name"]
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get modid...")
                    m.modid = mod["modid"]
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get version...")
                    m.version = mod["version"]
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get mcversion...")
                    m.mc_version = mod["mcversion"]
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get name...")
                    m.update_url = mod["updateJSON"]
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get description...")
                    m.description = mod["description"]
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get credits...")
                    m.credits = mod["credits"]
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get required mods...")
                    for modid in mod["requiredMods"]:
                        self._add_mod_dependency(m, modid)
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get dependencies...")
                    for modid in mod["dependencies"]:
                        self._add_mod_dependency(m, modid)
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get authors... (from authors)")
                    for author in mod["authors"]:
                        self._add_mod_author(m, author)
                except KeyError:
                    self.logger.debug("Attempt failed")

                try:
                    self.logger.debug("Trying to get authors... (from authorList)")
                    for author in mod["authorList"]:
                        self._add_mod_author(m, author)
                except KeyError:
                    self.logger.debug("Attempt failed")

                self.mods.append(m)
        except Exception as ex:
            self.logger.warning("Adding of mod failed due to: {}".format(type(ex), ex.args))
            raise exceptions.ModInfoNotExistError()
        else:
            self.logger.debug("Addition successful!")
            self.mods.pop(0)  # remove the empty entry at the start

    def _add_mod_author(self, m, author):
        """
        Adds a mod author
        :param m: Mod
        :param author: String
        :return: None
        """
        self.logger.debug("Adding a new Author: {}".format(author))
        x = ModAuthor(author)
        db_session.add(x)
        db_session.commit()

        m.authors.append(x)
        self.logger.debug("Successfully added Author")

    def _add_mod_dependency(self, m, modid):
        """
        Adds a mod dependency
        :param m: Mod
        :param modid: String
        :return: None
        """
        self.logger.debug("Looking up DepMod for modid: {}".format(modid))
        x = DepMod.query.get(modid)
        if x is None:
            self.logger.debug("DepMod doesn't yet exist, creating one")
            x = DepMod(modid)
            db_session.add(x)
            db_session.commit()
            self.logger.debug("Added to database successfully")

        m.dependencies.append(x)
        self.logger.debug("Successfully added dependency")

    def __repr__(self):
        return '<MCModFile Mods: {}>'.format(self.mods)


def add(file, dl_url=None, curse_id=None, curse_file_id=None, ignore_modexist_error=False):
    """
    handles mod adding
    :param file: string, absolute path to the modfile (located somewhere temporarily, in APPLICATION_ROOT/tmp/uploads/<file>)
    :return: int, id of the mod
    """
    logger.info("Adding mod from file: {} and dl_url: {}".format(file, dl_url))

    # 1. check if it has mcmod.info
    logger.info("Attempting to load McMod Info")
    info = attempt_load_mcmodinfo(file)

    logger.info("Found mcmodinfo to be: {}".format(info))

    if info is not None:
        logger.info("Info exists!")
        # we can work with mcmod.info data
        logger.info("Loading Information into MCModFile")
        mod_file_data = MCModFile(info)
        mod_file_data.populate()
    elif curse_id:
        logger.warning("No MCModInfo was found, but mod is from Curse, so using Curse data instead...")
        mod_file_data = MCModFile()

        curse_mod = simple_mod_installer.searchmods.cursemods.get_from_id(curse_id)
        if curse_mod is not None:
            logger.info("Curse mod found: {}".format(curse_mod))
            mod_file_data.mods = [MCMod(
                name=curse_mod.name
            )]
        else:
            logger.info("Curse mod was not found in database")
    else:
        logger.warning("No MCModInfo Found")
        # There is no mcmod.info data
        logger.info("Creating empty MCModFile")
        mod_file_data = MCModFile()

    logger.info("Continuing addition of Mod")
    return _add_after_infoparse(file, mod_file_data, dl_url, ignore_modexist_error=ignore_modexist_error, curse_id=curse_id, curse_file_id=curse_file_id)  # hand off the execution


def _add_after_infoparse(file, info, dl_url, ignore_modexist_error=False, curse_id=None, curse_file_id=None):
    """
    Does things after parsing of the file
    :param file: string, absolute path to the modfile (located somewhere temporarily, in APPLICATION_ROOT/tmp/uploads/<file>)
    :param info: MCModFile
    :param dl_url: string, URL the mod was downloaded from, if it was acquired via direct DL
    :param ignore_modexist_error: bool, whether or not to ignore the ModExistsError
    :return: int, id of the mod
    """
    # 1. Move the file in to the mod folder

    # i. ensure that the directory exists
    logger.info("Creating directories as required")
    os.makedirs(
        join_path(
            config["application_root"],
            "mods"
        ),
        exist_ok=True
    )

    # ii. Check if the file already exists:
    final_filename = get_file_name(file)
    final_filepath = join_path(
                        config["application_root"],
                        "mods",
                        final_filename
                    )
    logger.info("Determined path for mod file to be: {}".format(final_filepath))

    if os.path.exists(final_filepath):
        try:
            logger.warning("Final path exists! Figuring out what to do...")
            # it is already present in the directory. Compare the files
            logger.debug("Found filename of path: {} to be: {}".format(file, get_file_name(file)))
            for existing in Mod.query.filter(or_(Mod.filename == get_file_name(file), Mod.modid.in_([i.modid for i in info.mods]))).all():
                # for every mod with the same filename, or with the same modid.
                #logger.debug("Found matching mod in database: {}".format(existing))
                for mod in info.mods:
                    logger.debug("Checking existing mod: {} against {} found in modfile".format(existing, mod))
                    if existing.modid == mod.modid and existing.version == mod.version:
                        # they are the same mod, at the same version. Do they want a double up?
                        logger.error("Mod file has the same modid, at the same version")
                        raise exceptions.ModExistsError(existing.id)
                else:
                    continue
            else:
                logger.info("No exact match for name and version exists in our database. Generating a unique file name...")
                # they're different. Fix the naming thing
                final_filename = find_unique_name(
                        join_path(config["application_root"], "mods"),
                        get_file_name(file)
                    )

                final_filepath = join_path(
                    config["application_root"],
                    "mods",
                    final_filename
                )

        except exceptions.ModExistsError:
            if not ignore_modexist_error:
                # clean up the mod file from temp
                logger.warning("ignore_modexist_error flag set to False, so cancelling operation.")
                try:
                    logger.debug("Attempting to clean up modfile at: {}".format(file))
                    os.unlink(file)
                except OSError:
                    logger.warning("Failed to clean modfile at: {}".format(file))
                    pass

                raise
            else:
                # We think that this is a duplicate, but we've been told to add it anyway so, generate new filename
                logger.info("ignore_modexist_error flag set to True, so continuing operation with renamed file.")
                # fix the file naming thing
                final_filename = find_unique_name(
                    join_path(config["application_root"], "mods"),
                    get_file_name(file)
                )

                final_filepath = join_path(
                    config["application_root"],
                    "mods",
                    final_filename
                )

    # iii. perform the move
    logger.info("Moving {} to {}".format(file, final_filepath))
    shutil.move(  # shutil because it can handle operations across disks (e.g. C drive to F drive) unlike os.rename
        file,
        final_filepath
    )
    logger.info("Move successful. Adding mods to database...")

    # 2. Add to db
    if info.mods:
        logger.debug("Mods present, beginning add...")
        info.add_to_database(final_filename, dl_url, curse_id=None, curse_file_id=None)
    else:
        logger.error("No Mods are found in the mod file")
        raise exceptions.ModNotExistError()

    logger.info("Finished adding mod file.")

    return Mod.query.order_by(Mod.id.desc()).first().id


def remove(id):
    """
    Removes a mod from the filesystem and database, including deletion of all links to collections
    :param id: int
    :return: None
    """
    logger.info("Beginning removal of mod with id: {}".format(id))

    # 0. Get file name:
    logger.debug("Getting Mod from database...")
    m = Mod.query.get(id)

    if m is None:
        logger.error("Mod doesn't exist in database")
        raise exceptions.ModNotExistError(id)

    filename = m.filename

    if filename is None:
        logger.critical("Database entry is missing mission-critical filename data. Throwing error...")
        raise exceptions.ModInfoNotExistError(id, 'filename')

    # 1. Remove all symlinks in Collections
    logger.info("Removing from collections: {}".format(m.collections))
    for coll in m.collections:
        logger.debug("Working with collection {}...".format(coll.id))
        logger.debug("Removing Symbolic link...")
        try:
            os.unlink(join_path(
                config["application_root"],
                "collections",
                coll.mc_id.decode(),
                "mods",
                filename
            ))
        except FileNotFoundError as ex:
            logger.error("Symlink doesn't exist")
        except OSError as ex:
            logger.critical("Insufficient Permissions for Symbolic link manipulation: {}".format(ex.args))

        logger.debug("Symlink removed successfully")

        logger.debug("Removing relationship...")
        coll.rem_mod(m)
        logger.debug("Relationship removed")

    logger.info("Finished removing from collections")

    # 2. Delete mod file:
    logger.info("Deleting mod file...")
    os.remove(join_path(
        config["application_root"],
        "mods",
        filename
    ))
    logger.info("Deletion successful")

    # 3. Delete Mod from database
    logger.info("Removing from database...")
    for mod in Mod.query.filter(Mod.filename == m.filename):
        logger.debug("Removing mod: {!r} from database".format(mod))
        db_session.delete(mod)
    logger.info("Removed")

    logger.debug("Committing Database changes...")
    db_session.commit()
    logger.debug("Commit successful")

    logger.info("Finished Removing mod with id {}".format(id))


def get_from_id(id):
    """
    Gets a Mod from it's id
    :param id: int
    :return: Mod
    """
    m = Mod.query.get(id)
    if m is not None:
        return m
    else:
        raise exceptions.ModNotExistError(id)


def all():
    """
    Gets all mods
    :return: list
    """
    return Mod.query.all()
