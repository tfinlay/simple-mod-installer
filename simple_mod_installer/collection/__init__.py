"""
Everything to do with Collections.

This module brings everything from the other modules together to provide a nice api for collection-based things
"""
import sqlalchemy
from sqlalchemy import and_, or_
import os
import copy
import shutil
import logging#, logging.config
from simple_mod_installer.database.models import Collection, Mod
from simple_mod_installer.database import db_session
from simple_mod_installer import config
from simple_mod_installer.util import join_path, create_symbolic_link, get_file_name
from simple_mod_installer import exceptions
import simple_mod_installer.mc_interface as mc_interface
from simple_mod_installer.collection import checks


#logging.config.dictConfig(config["logging"])
logger = logging.getLogger(__name__)


def name_exists(name):
    """
    Checks whether a specific name is taken
    :param name: string
    :return: bool
    """
    (ret,), = db_session.query(sqlalchemy.exists().where(Collection.name == name))
    return ret


def _create_collection_filesystem(root, mc_id, folders=("mods", "config", "saves", "resourcepacks")):
    """
    Creates the filesystem for a Collection
    :param root: string, the location which contains all Collections' folders
    :param mc_id: string, the mc_id of the collection
    :param folders: tuple<string>, all of the subfolders to create for the collection
    :return: string, absolute path to the collection's root folder
    """
    # create the path up to <root>/<name>/
    coll_root = join_path(root, mc_id.decode())
    print("Creating Folder: {}".format(coll_root))

    if os.path.exists(coll_root):
        shutil.rmtree(coll_root)
    os.makedirs(coll_root)

    for folder in folders:
        # create all of the sub folders for this collection
        os.mkdir(
            join_path(
                coll_root,
                folder
            )
        )

    return coll_root  # e.g. /tfff1/SimpleLauncher/collections/<name> or C:\tfff1\SimpleLauncher\collections\<name>


def add(name, mcversion, version_id):
    """
    Adds a new collection (if it doesn't exist already) to the DB, Minecraft, & the FileSystem
    :param name: string, user-friendly name of the Collection
    :param mcversion: string, general Minecraft Version for the collection. e.g. 1.7.10
    :param version_id: string, exact name of a specific version of minecraft. e.g. 1.7.10-Forge10.13.4.1558-1.7.10
    :return: int, id of the newly created Collection
    """
    logger.info("Adding collection: {}, {}, {}".format(name, mcversion, version_id))
    if not name_exists(name):  # if a Collection by this name doesn't yet exist:
        # 1. Add it to the database
        logger.info("Adding to database")
        c = Collection(name, mcversion, version_id)
        db_session.add(c)
        db_session.commit()
        logger.info("Committed to database")

        # 2. Creates it's directory and filesystem
        logger.info("Creating filesystem...")
        coll_loc = _create_collection_filesystem(
            join_path(
                config["application_root"],
                "collections"
            ),
            c.mc_id
        )
        logger.info("Filesystem created")

        # 3. Add it to Minecraft as a Profile
        logger.info("Adding Minecraft Profile")
        prof = mc_interface.Profile(
            c.mc_id,
            name,
            version_id,
            coll_loc
        )
        prof.commit()
        logger.info("New Profile committed")

        print(mc_interface.Profile(
            c.mc_id,
            name,
            version_id,
            coll_loc
        ).dictify()
                    )

        return c.id
    else:
        logger.error("A Collection with the name: {} already exists".format(name))
        raise exceptions.CollectionExistsError(
            str(Collection.query.filter(Collection.name == name).first().id)
        )


def remove(id):
    """
    Removes a collection with id
    :param id: int, id of the collection to be removed
    :return: string, the name of the Collection which has been deleted
    """
    logger.info("Removing Collection with id: {}".format(id))
    # 0. Look up in database
    c = Collection.query.get(id)

    if c is not None:  # if it exists then:
        logger.info("Found Collection")
        # 1. Remove from launcher_profiles.json
        logger.info("Removing Profile from Minecraft Profiles")
        mc_interface.rem_profile(c.mc_id)

        name = copy.copy(c.name)
        dir_loc = copy.copy(c.get_collection_path())

        logger.info("Removing from database")
        Collection.query.filter(Collection.id == id).delete()

        db_session.commit()

        # 2. Remove from Filesystem
        logger.info("Removing from filesystem at: {}".format(dir_loc))

        shutil.rmtree(dir_loc)

        logger.info("Finished removing Collection: {}".format(name))

        return name
    else:
        logger.error("Collection with id: {} doesn't exist".format(id))
        raise exceptions.CollectionNotExistError(id)


def get_from_id(id):
    """
    Gets a collection from it's id
    :param id: int
    :return: Collection
    """
    c = Collection.query.get(id)
    if c is not None:
        return c
    else:
        raise exceptions.CollectionNotExistError(id)


def all():
    """
    Returns an array containing all collections
    :return: tuple<Collection>
    """
    return tuple(Collection.query.all())


# TODO: finish this:
def get(**kwargs):
    """
    Gets collection(s) based on what we already know about it/them
    :param kwargs:
    :return: list<Collection>
    """
    if 'id' in kwargs.keys():
        Collection.query.get(kwargs["id"])
    elif 'name' in kwargs.keys():
        Collection.query.filter(Collection.name == kwargs)


def add_mod(collection_id, mod_id):
    """
    Adds a mod to a collection
    :param collection_id: int
    :param mod_id: int
    :return: None
    """
    try:
        collection_id = int(collection_id)
    except ValueError:
        logger.critical("Collection id is not a valid integer")
        raise

    try:
        mod_id = int(mod_id)
    except ValueError:
        logger.critical("Mod id is not a valid integer")
        raise

    logger.info("Adding mod {} to collection {}".format(mod_id, collection_id))
    coll = Collection.query.get(collection_id)
    mod = Mod.query.get(mod_id)

    if mod is not None and coll is not None:
        logger.info("Beginning addition...")

        # 1. Create symlink
        logger.info("Creating Symbolic link...")
        try:
            create_symbolic_link(
                join_path(
                    config["application_root"],
                    "mods",
                    mod.filename
                ),
                join_path(
                    config["application_root"],
                    "collections",
                    coll.mc_id.decode(),
                    "mods",
                    get_file_name(mod.filename)
                )
            )
        except FileExistsError:
            logger.warning("File already exists, continuing...")

        logger.info("Symlink created")

        # 2. Add relationship to database, for all mods in this file
        for m in Mod.query.filter(Mod.filename == mod.filename):
            logger.debug("Adding mod: {!r} to collection: {!r} in database".format(m, coll))
            coll.add_mod(m)
        db_session.commit()
        logger.info("Mod added successfully")
    elif mod is None:
        logger.error("Mod does not exist")
        raise exceptions.ModNotExistError(mod_id)
    else:
        logger.error("Collection does not exist")
        raise exceptions.CollectionNotExistError(collection_id)


def rem_mod(collection_id, mod_id):
    """
    Removes a mod from the collection
    :param collection_id: int, the id of the collection
    :param mod_id: int, id of the mod
    :return: None
    """
    try:
        collection_id = int(collection_id)
    except ValueError:
        logger.critical("Collection id is not a valid integer")
        raise

    try:
        mod_id = int(mod_id)
    except ValueError:
        logger.critical("Mod id is not a valid integer")
        raise

    logger.info("Removing mod with id: {} from collection with id: {}".format(mod_id, collection_id))
    coll = Collection.query.get(collection_id)
    mod = Mod.query.get(mod_id)
    if mod is not None and coll is not None:
        logger.info("Mod and Collection exist, proceeding to removal...")
        if mod in coll.mods:  # check if the mod is in this collection
            logger.info("Removing symbolic link...")
            try:
                os.unlink(
                    join_path(
                        config["application_root"],
                        "collections",
                        coll.mc_id.decode(),
                        "mods",
                        get_file_name(mod.filename)
                    )
                )
            except FileNotFoundError:
                logger.warning("Symlink already missing, continuing...")

            logger.info("Symlink removed")

            logger.info("Removing link from database...")
            for m in Mod.query.filter(and_(Mod.collections.any(id=collection_id), Mod.filename == mod.filename)):
                logger.debug("Removing Mod: {!r}".format(m))
                coll.rem_mod(m)
            db_session.commit()
            logger.info("Database commit successful")
        else:
            logger.error("Mod is not in this collection, no action required")

        logger.info("Mod removal successful")
    elif mod is None:
        logger.error("Mod does not exist")
        raise exceptions.ModNotExistError(mod_id)
    else:
        logger.error("Collection doesn't exist")
        raise exceptions.CollectionNotExistError(collection_id)
