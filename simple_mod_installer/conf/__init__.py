"""
migrated from conf.py
"""
from collections import OrderedDict
from simple_mod_installer.util import join_path, get_default_mc_loc, get_default_tfff1_loc, ensure_dirs_exist, get_parent_dir
import json
import os
from os.path import dirname, abspath, isfile
import logging
from .migrator import CONFIG_UPDATERS


class ConfigUpdateError(Exception):
    pass

logger = logging.getLogger(__name__)

VERSIONS = ["1.0", "1.1"]
HISTORIC_CONFIG_LOCATIONS = [  # the zero'th item should be the current location
    # from latest to oldest
    join_path(get_default_tfff1_loc(), "SimpleLauncher", "config.json"),
    join_path(dirname(dirname(abspath(__file__))), "config.json")
]


DEFAULT_CONFIG = {
    "version": "1.1",
    "application_root": join_path(get_default_tfff1_loc(), 'SimpleLauncher'),
    "minecraft_directory": get_default_mc_loc(),
    "fetch_curse_moddata": True,
    "database_path": join_path(get_default_tfff1_loc(), 'SimpleLauncher', 'moddata.sqlite'),
    "webserver_port": 4000,
    "logging": {
        "version": 1,
        "formatters": {
            "f": {"format": "(%(name)s) [%(levelname)s]: %(message)s"}
        },
        "handlers": {
            'fh': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'f',
                'level': logging.INFO,
                'maxBytes': 1000000,
                'backupCount': 1,
                'filename': 'simple.log'
            },
            'sh': {
                'class': 'logging.StreamHandler',
                'formatter': 'f',
                'level': logging.INFO
            }
        },
        'root': {
            'handlers': ['fh', 'sh'],
            'level': logging.INFO
        },
        'loggers': {
            'DEEP_DEBUG': {
                'level': 1
            }
        }
    }
}


def is_latest_version(config):
    """
    checks whether the loaded config is up-to-date
    :param config: dict, config file
    :return: pair<bool, string>, whether the config is up to date or not & the config version
    """
    logger.debug("checking config file version...")
    if config["version"] != VERSIONS[-1]:
        logger.warning("Config file is an old format (version: {}). Latest is: {}.".format(config["version"], VERSIONS[-1]))
        return False, config["version"]
    else:
        logger.debug("Config is up to date (version {})".format(VERSIONS[-1]))
        return True, config["version"]


def update_config(config_loc, current_version):
    """
    upgrades old versions of the config for the modern era
    :param config_loc: string, absolute path to config file
    :param current_version: string, current config version
    :return: None
    """
    logger.info("updating config file at: {} to latest version: {}, from: {}".format(config_loc, VERSIONS[-1], current_version))
    depth = 0
    while current_version != VERSIONS[-1]:
        if depth > len(VERSIONS):
            # something has gone wrong here...
            logger.error("update_config method has iterated more times than there have been config versions, maybe an infinite loop? Terminating")
            raise ConfigUpdateError()
        try:
            current_version = CONFIG_UPDATERS[current_version](config_loc)
        except KeyError:
            logging.error("Old version: {} wasn't found so update failed.".format(current_version))
            raise ConfigUpdateError()

        depth += 1
        logger.debug("Finished update to config v{} (depth: {})".format(current_version, depth))

    logger.info("Finished config update!")


def get_config(config_loc=None):
    if config_loc is None:
        logger.info("finding config...")
        # try every normal location
        for loc in HISTORIC_CONFIG_LOCATIONS:
            logger.debug("Trying path: {}".format(loc))
            if isfile(loc):
                logger.debug("Found file!")
                # here's the config
                return Config(config_loc=loc)

        logger.debug("Failed to find config, setting location to: {}".format(HISTORIC_CONFIG_LOCATIONS[0]))

        # haven't found any config files so I guess this is a new installation
        return Config(config_loc=HISTORIC_CONFIG_LOCATIONS[0])


class Config:
    def __init__(self, config_loc):
        # type: (str) -> None
        self.config_loc = config_loc

        if not os.path.exists(self.config_loc):
            ensure_dirs_exist(get_parent_dir(self.config_loc))

            print("Config file doesn't exist. Creating...")
            with open(self.config_loc, 'w') as f:
                json.dump(DEFAULT_CONFIG, f)

        with open(self.config_loc) as config_file:
            self.json = json.load(config_file)

        is_latest, current_version = is_latest_version(self.json)

        if not is_latest:
            logger.debug("Config isn't at latest version...")
            update_config(self.config_loc, current_version)
            self.reload()

    def reload(self):
        logger.info("Reloading config...")
        with open(self.config_loc) as config_file:
            self.json = json.load(config_file)

    def __getitem__(self, item):
        return self.json[item]

    def __setitem__(self, key, value):
        self.json[key] = value

        with open(self.config_loc, 'w') as configfile:
            json.dump(self.json, configfile)
