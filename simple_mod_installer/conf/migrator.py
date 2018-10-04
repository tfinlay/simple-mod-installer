"""
These functions migrate from the key version up to the config version specified by the function's return value.

Each function takes one parameter: an absolute path to the config file
"""
import json
from simple_mod_installer.util import join_path
import logging

logger = logging.getLogger(__name__)


def update_1_0_to_1_1(config_file_path):
    # type: (str) -> str
    print("upgrading from version 1.0 to 1.1...")
    logging.debug("upgrading from version 1.0 to 1.1...")
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    # add new values (set to default)
    config["database_path"] = join_path(config["application_root"], "moddata.sqlite")
    config["webserver_port"] = 4000

    # remove unneeded values

    # update modified values
    config["version"] = "1.1"

    # write out again
    with open(config_file_path, 'w') as f:
        json.dump(config, f)

    return "1.1"


CONFIG_UPDATERS = {
    "1.0": update_1_0_to_1_1,
}
