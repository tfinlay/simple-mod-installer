"""
All checks done to mods within a collection
"""
import logging
from collections import defaultdict
from sqlalchemy import and_
from simple_mod_installer.database.models import Mod

logger = logging.getLogger(__name__)


IGNORED_DEPENDENCIES = ("Forge", "mod_MinecraftForge")


def mod_mcversion_check(mod, collection):
    """
    Checks if the mod and collection share the same mcversion
    :param mod: Mod
    :param collection: Collection
    :return: bool, True if they do, else False
    """
    if (not mod.mc_version) or mod.mc_version == collection.mc_version:
        return True
    else:
        return False

    logger.debug(mod.mc_version == collection.mc_version and True if mod.mc_version else False)
    return mod.mc_version == collection.mc_version and False if mod.mc_version else True  # ignore the issue if the mod has not mcversion data


def mcversion_check(collection):
    """
    Checks for any issues with mcversions  with mods in a Collection
    :param collection: Collection
    :return: array<String>, all of the mcversion issues
    """
    issues = []
    for mod in collection.mods:
        if not mod_mcversion_check(mod, collection):
            logger.debug("Mod: {} doesn't have the same mcversion as collection: {}".format(mod, collection))
            issues.append(mod.id)

    return issues


def dependency_check(collection, group_by_dependency=False):
    """
    Checks for any issues with dependencies with mods in a Collection, grouping them by dependency id, or by affected mod id
    :param collection: Collection
    :param group_by_dependency: bool, whether or not to group results by dependency
    :return: array<String>, all of the missing dependencies
    """
    logger.info("Starting dependency checking for collection: {}".format(collection))
    errors = defaultdict(list)

    for mod in collection.mods:
        for m in mod.dependencies:
            logger.debug("Looking for dependency: {} in {}".format(m, collection.mods))
            if m.modid not in IGNORED_DEPENDENCIES:
                if Mod.query.filter(and_(Mod.modid == m.modid, Mod.id.in_([x.id for x in collection.mods]))).all():
                    # If there is a Mod with this m's modid and it's in this collection, then:
                    logger.debug("Dependency found!")
                else:
                    logger.debug("Dependency not found!")

                    errors[m.modid].append(mod.id) if group_by_dependency else errors[mod.id].append(m.modid)
            else:
                logger.debug("dependency is to be ignored (it's in IGNORED_DEPENDENCIES)")
    return errors


def mod_dependency_check(mod, collection):
    """
    !!DEPRECATED!! - Merged into dependency_check
    Checks if this mod has all of it's dependencies fulfilled
    :param mod: Mod
    :param collection: Collection
    :return: bool
    """
    logger.info("Checking dependencies for {} in {}".format(mod, collection))

    dep_problems = []

    for m in mod.dependencies:
        logger.debug("Looking for dependency: {} in {}".format(m, collection.mods))

        if Mod.query.filter(and_(Mod.modid == m.modid, Mod.id.in_([x.id for x in collection.mods]))).all():
            # If there is a Mod with this m's modid and it's in this collection, then:
            logger.debug("Dependency found!")
        else:
            dep_problems.append(m.modid)
            logger.debug("Dependency not found!")

    return dep_problems
