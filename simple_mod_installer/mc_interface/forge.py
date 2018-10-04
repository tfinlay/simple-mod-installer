#import json
import logging
import urllib.request
import urllib.error
from . import get_versions
from simple_mod_installer.util import http

logger = logging.getLogger(__name__)

# populate this when required
FORGE_PROMOTION_URL = "https://files.minecraftforge.net/maven/net/minecraftforge/forge/promotions_slim.json"
MINECRAFT_RELEASES_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
_forge_promotions_maybe = None
_minecraft_releases_maybe = None


def get_forge_promotions():
    """
    Raw dict of Forge promotions
    :return: dict, see: http://files.minecraftforge.net/maven/net/minecraftforge/forge/promotions_slim.json
    """
    global _forge_promotions_maybe
    logger.debug("Getting forge promotions")
    if _forge_promotions_maybe is not None:
        logger.debug("Already downloaded promotions")
    else:
        logger.info("Attempting to fetch forge promotions...")
        try:
            response = urllib.request.urlopen(FORGE_PROMOTION_URL)
        except urllib.error.URLError as ex:
            logger.error("Failed to fetch Forge promotions, URLError: {} occurred".format(ex))
        else:
            if response.getcode() == 200:
                _forge_promotions_maybe = http.load_json_from_response(response)
            else:
                return dict(promos=dict())
                logger.warning("Failed to load Minecraft releases, maybe the server is temporarily offline?")

    return _forge_promotions_maybe


def get_minecraft_releases():
    """
    Raw dict of Minecraft releases
    :return: dict, see: https://launchermeta.mojang.com/mc/game/version_manifest.json
    """
    global _minecraft_releases_maybe
    logger.debug("Getting Minecraft releases...")
    if _minecraft_releases_maybe is not None:
        logger.debug("Already downloaded releases")
    else:
        logger.info("Attempting to fetch Minecraft releases...")
        try:
            response = urllib.request.urlopen(MINECRAFT_RELEASES_URL)
        except urllib.error.URLError as ex:
            logger.error("Failed to fetch Minecraft releases, URLError: {} occurred".format(ex))
        else:
            if response.getcode() == 200:
                _minecraft_releases_maybe = http.load_json_from_response(response)
            else:
                logger.warning("Failed to load Minecraft releases, maybe the server is temporarily offline? If this problem persists contact a maintainer")

    return _minecraft_releases_maybe


def parse_local_forge_version(v):
    """
    Parses locally installed Version and returns the information contained within
    :param v: mc_interface.Version
    :return: dict
    """
    d = dict()
    if "forge" in v.id().lower():
        logger.debug("Detected Forge Profile with id: {}".format(v.id()))
        # it's a forge profile
        d["moddable"] = True
        split_data = v.id().lower().split('-')

        if len(split_data) < 3:
            logger.error("Parsed invalid forge profile signature. Split into only {} pieces. Regarding as Vanilla.".format(len(split_data)))
            return dict(moddable=False, mc_version="0.0.0")

        # should split in to 3 parts: mcversion, ForgeVersion, mcversion OR 3 like: mcversion, ForgeMcVersion, forgeVersion
        d["mc_version"] = split_data[0]

        second_without_forge = split_data[1].replace("forge", "")
        if len(split_data[1]) > len(split_data[2]):
            # index 1 has the forge version number
            d["forge_version"] = split_data[1]
        else:
            # index 2 has the forge version number
            d["forge_version"] = split_data[2]
    else:
        logger.debug("Detected Vanilla Profile with id: {}".format(v.id()))
        # let's assume it's a vanilla profile
        d["moddable"] = False
        if v.id().lower()[0] == 'b':
            logger.debug("Vanilla profile is beta")
            d["mc_version"] = v.id()[1:]
        else:
            d["mc_version"] = v.id()

    return d


def _default_version_name_formatter(mc_version, moddable, currently_installed):
    # type: (str, bool, bool) -> str
    """
    Formats a mod into a user-displayable string
    :param mc_version: string
    :param moddable: bool
    :param currently_installed: bool
    :return: string
    """
    if moddable:
        return "Forge {}{}".format(mc_version, "" if currently_installed else " (downloadable)")
    else:
        return "Minecraft {}{}".format(mc_version, "" if currently_installed else " (downloadable)")


def get_available_minecraft_releases(version_name_formatter=_default_version_name_formatter):
    """
    Gets a list of all of the valid versions which are available for download or installation from Mojang AND have recommended releases for Forge
    :param version_name_formatter: function which accepts arguments: mc_version (string), moddable (bool), currently_installed (bool) and returns a String
    :return: dict<list<dict<name (string), currently_installed (bool)> > >
    """
    def filter_to_recommended(forge_vs):
        allowed = []
        for v in forge_vs:
            if v == "latest" or v == "recommended":
                continue

            if "recommended" in v:
                allowed.append(v.split('-')[0])

        return allowed

    local_versions = [parse_local_forge_version(v) for v in get_versions()]
    forge_versions = set(filter_to_recommended(get_forge_promotions()["promos"].keys()))
    #_mc_vs = get_minecraft_releases()["versions"]
    #print(_mc_vs)
    #print([v["id"] for v in _mc_vs])
    minecraft_versions = set([v["id"] for v in get_minecraft_releases()["versions"]])

    if len(forge_versions) == 0 and len(minecraft_versions) == 0:
        logger.warning("Forge versions and Minecraft versions haven't downloaded, so there's no point doing any checking")

    to_return = dict(
        moddable=[],  # aka Forge
        vanilla=[]
    )  # type: {str, [dict()]}

    '''
    to_return e.g.
    
    {
        moddable: [
            {
                name: "Forge 1.7.10",
                currently_installed: True
            }
        ],
        vanilla: [
            {
                name: "Minecraft 1.7.10",
                currently_installed: True
            }
        ]
    }
    '''

    for version in local_versions:
        # remove every vanilla version which is already installed from minecraft_versions or doesn't have a Forge download available
        if version["mc_version"] in minecraft_versions:
            minecraft_versions.remove(version["mc_version"])

        if version["moddable"]:
            # remove the Forge listing as well, because this profile is Forge
            logger.debug("Attempting to remove forge_version: {} from forge_versions since it's already installed".format(version["mc_version"]))
            try:
                forge_versions.remove(version["mc_version"])
            except KeyError:
                logger.debug("Removal of forge version failed")

            to_return["moddable"].append(dict(
                name=version_name_formatter(version["mc_version"], True, True),  # we're only looping over installed profiles
                currently_installed=True
            ))
        else:
            to_return["vanilla"].append(dict(
                name=version_name_formatter(version["mc_version"], version["moddable"], True),  # we're only looping over installed profiles
                currently_installed=True
            ))

    # loop over every remaining Minecraft & Forge version...
    for mc_version in sorted(minecraft_versions, reverse=True):
        to_return["vanilla"].append(dict(
            name=version_name_formatter(mc_version, False, False),  # we're only looping over installed profiles
            currently_installed=False
        ))

    for forge_mc_version in sorted(forge_versions, reverse=True):
        to_return["moddable"].append(dict(
            name=version_name_formatter(forge_mc_version, True, False),  # we're only looping over installed profiles
            currently_installed=False
        ))

    return to_return
