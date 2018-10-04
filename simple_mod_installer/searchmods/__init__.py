"""
Searches mod databases for matches
"""
import logging
from sqlalchemy import or_, and_
from simple_mod_installer.database.models import Mod, Collection
from simple_mod_installer import collection, exceptions
from .cursemods import curse_mods_lock, curse_mods
from .util import match_cursemod_db

logger = logging.getLogger(__name__)


class SearchMod:
    def __init__(self, name, versions, local_id=None, curse_id=None, authors=()):
        """
        :param name: string, name of the mod
        :param versions: dict<mc_version, dict<dl_url, installed>, all of the version that this mod supports, their download links, and whether that version is installed
        :param curse_id: string, id of the mod on curse
        """
        self.name = name
        self.versions = versions

        self.local_id = local_id
        self.curse_id = curse_id

        self.authors = authors

    def jsonify(self):
        return dict(
            name=self.name,
            versions=self.versions,
            curse_id=self.curse_id,
            local_id=self.local_id,
            authors=self.authors
        )


def raw_search(term=None, context=None, search_local=True, search_remote=True):
    """
    Parses the raw request data into searchable info
    :param term: String
    :param context: String
    :return: array<SearchMod>
    """
    logger.info("Starting mod search with term: {}, context: {}".format(term, context))

    if not term:
        logger.debug("Term is undefined. Setting to ''")
        term = ""

    if context:
        logger.debug("Attempting to get collection with specified id")
        try:
            context = collection.get_from_id(context)
        except exceptions.CollectionNotExistError:
            logger.warning("Tried to find collection with id: {}, but none was found. Continuing search without collection.".format(context))
            context = None

    # go into the process
    return search(term, context, search_local, search_remote)


def get_curse_mods(term, context=None, max_matches=20):
    """
    Uses the curse search API for searching
    :param term: String
    :param context: Collection
    :param max_matches: int
    :return: array<SearchMod>, the first 20 mods, in the order sent by CurseForge
    """

    matches = []

    logger.info("Acquiring curse_mods lock...")
    with curse_mods_lock:
        logger.info("curse_mods lock acquired, beginning search...")
        for mod in curse_mods:
            logger.log(1, "Checking curse mod: {}".format(mod))
            if len(matches) == max_matches:
                break

            if term.lower() in mod.name.lower() and len(mod.files) > 0:
                logger.debug("Found curse mod: {}".format(mod))

                mod_data = {}

                def context_modsearch():
                    # Check if this is installed here already
                    local_mods = match_cursemod_db(mod)

                    for m in local_mods:
                        if m.curse_file_id not in [x.id for x in mod.files] and m not in context.mods:
                            logger.debug("Found curse mod file: {}".format(m))
                            for file in reversed(mod.files):
                                logger.debug("Found file: {}".format(file))
                                for v in file.game_versions:
                                    logger.debug("Found version: {}".format(v))
                                    if v == context.mc_version:
                                        mod_data[v] = dict(
                                            dl_url=file.download_url,
                                            installed=False,
                                            file_id=file.id
                                        )

                            matches.append(SearchMod(
                                name=mod.name,
                                versions=mod_data,
                                curse_id=mod.id,
                                authors=mod.authors
                            ))
                    else:
                        no_context_modsearch()

                def no_context_modsearch():
                    for file in reversed(mod.files):  # iterate backwards to ensure the latest file overwrites those before it if need be.
                        v_count = 0
                        logger.debug("File: {}'s game versions are: {}".format(file, file.game_versions))
                        for version in file.game_versions:
                            v_count += 1
                            mod_data[version] = dict(
                                dl_url=file.download_url,
                                installed=False,
                                file_id=file.id
                            )

                        if v_count == 0:
                            # Create a version for this file
                            mod_data["*"] = dict(
                                dl_url=file.download_url,
                                installed=False,
                                file_id=file.id
                            )

                    # print(mod_data)

                    matches.append(SearchMod(
                        name=mod.name,
                        versions=mod_data,
                        curse_id=mod.id,
                        authors=mod.authors
                    ))

                if context:
                    context_modsearch()
                else:
                    no_context_modsearch()

    return matches


def get_local_mods(term, context=None):
    """
    Gets and orders all of the matching mods from our local database, removes those in the Collection already if a context is specified.
    :param term: String
    :param context: Collection
    :return: array<SearchMod>, all of the matching mods in our local database, ordered according to the _super groovy_ algorithm for ranking things
    """
    logger.info("Searching local mods with term: `{}` and context: {}".format(term, context))
    term = "%{}%".format(term)
    if not context and term == "%%":  # term is empty
        logger.debug("No context or term, getting all local mods")
        m = Mod.query.all()
    elif not context:
        logger.debug("No context, using term for local mods")
        m = Mod.query.filter(Mod.name.ilike(term)).all()
        m.extend(Mod.query.filter(and_(Mod.modid.ilike(term), Mod.id.notin_([mod.id for mod in m]))).all())
    elif not term:
        logger.debug("No term, using context to filter local mods")
        m = Mod.query.filter(Mod.id.notin_([m.id for m in context.mods])).all()
    else:
        logger.debug("Both context and term, using both")
        m = Mod.query.filter(and_(Mod.name.ilike(term), Mod.id.notin_([m.id for m in context.mods]))).all()
    logger.debug("Found {} out of all mods: {}".format(m, Mod.query.all()))

    logger.info("Found {} local mods".format(len(m)))

    def gen_version(mc_version, filename):
        return {mc_version: dict(installed=True, filename=filename)}

    return [SearchMod(
        name=mod.name,
        versions=gen_version(mod.mc_version, mod.filename),
        local_id=mod.id,
        authors=[str(author) for author in mod.authors]
    ) for mod in m]


def sort_with_context(term, context, item):
    """
    Give values to an item depending on it's relationship to the search term, and context Collection
    :param context: Collection
    :param item: SearchMod
    :return:
    """
    score = 0

    score += item.name in term

    matching_versions = []

    for i in item.versions.keys():
        if i == context.mc_version or i == '*':
            score += 1

    return score


def sort(term, item):
    """
    Give values to an item depending on it's relationship to the search term
    :param item: SearchMod
    :return: int
    """
    score = 0

    return score


def search(term, context=None, search_local=True, search_remote=True):
    """
    Entry point for a search
    :param term: String
    :param context: String
    :param search_local: bool, whether or not to search the local database for mods
    :param search_remote: bool, whether or not to search remote locations (Curse) for mods
    :return: array<SearchMod>, all of the matching mods, in order of relevance
    """
    #unsorted_results = get_curse_mods(term, context).extend(get_local_mods(term, context))
    logger.debug("Starting search with term: {}, context: {}, search_local: {}, search_remote: {}".format(
        term,
        context,
        search_local,
        search_remote
    ))

    unsorted_results = []

    if search_local:
        logger.info("Getting unsorted results from local mod database...")
        unsorted_results.extend(get_local_mods(term, context))

    if search_remote:
        logger.info("Getting unsorted results from Curse database...")
        unsorted_results.extend(get_curse_mods(term, context))

    logger.info("Sorting results...")

    if context:
        return sorted(unsorted_results, key=lambda item: sort_with_context(term, context, item))
    else:
        return sorted(unsorted_results, key=lambda item: sort(term, item))
