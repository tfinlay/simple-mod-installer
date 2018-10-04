from simple_mod_installer.util import join_path, get_default_mc_loc, get_default_tfff1_loc
import json
import os
from os.path import dirname, abspath
import logging


DEFAULT_CONFIG = {
    "version": "1.0",
    "application_root": join_path(get_default_tfff1_loc(), 'SimpleLauncher'),
    "minecraft_directory": get_default_mc_loc(),
    "fetch_curse_moddata": True,
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


class Config:
    def __init__(self, config_loc=join_path(dirname(abspath(__file__)), 'config.json')):
        self.config_loc = config_loc

        if not os.path.exists(self.config_loc):
            print("Config file doesn't exist. Creating...")
            with open(self.config_loc, 'w') as f:
                json.dump(DEFAULT_CONFIG, f)

        with open(self.config_loc) as config_file:
            self.json = json.load(config_file)

    def reload(self):
        with open(self.config_loc) as config_file:
            self.json = json.load(config_file)

    def __getitem__(self, item):
        return self.json[item]

    def __setitem__(self, key, value):
        self.json[key] = value

        with open(self.config_loc, 'w') as configfile:
            json.dump(self.json, configfile)
