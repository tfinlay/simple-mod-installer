"""
Interface for talking to the Minecraft client
"""
import datetime as dt
from simple_mod_installer.mc_interface import time
from simple_mod_installer.util import join_path
import json
from simple_mod_installer import config
from simple_mod_installer.database.models import Collection
import os, glob


class Profile:
    def __init__(self, id, name, version_id, game_dir, type="custom", created=time.to_mc_time(dt.datetime.now()), last_used=time.to_mc_time(dt.datetime.now())):
        """
        Represents a profile in launcher_profiles.json
        :param id: bytes, the SHA256 hashed version fo the name - unique
        :param name: string, Human-readable name of the profile
        :param version_id: string, id of the version of Minecraft used to run the profile
        :param game_dir: string, the location of the directory containing the profile
        :param type: string
        :param created: string, Minecraft-formatted datetime of profile creation
        :param last_used: string, Minecraft-formatted datetime of profile's last use
        """
        self.id = id
        self.name = name
        self.version_id = version_id
        self.game_dir = game_dir
        self.type = type
        self.created = created
        self.last_used = last_used

    def dictify(self):
        """
        Creates a launcher_profiles.json-style dictionary of this.
        :return: dict
        """
        return dict(
            name=self.name,
            type=self.type,
            created=self.created,
            lastUsed=self.last_used,
            lastVersionId=self.version_id,
            gameDir=self.game_dir
        )

    def commit(self, launcher_profile_loc=join_path(config["minecraft_directory"], "launcher_profiles.json")):
        """
        Saves profile to launcher_profiles.json, overwriting what previously had the same id as this
        :param launcher_profile_loc: string, absolute path to the launcher_profiles.json
        :return: None
        """
        with open(launcher_profile_loc) as data_file:
            tmp = json.load(data_file)

        tmp["profiles"][self.id.decode()] = self.dictify()

        with open(join_path(launcher_profile_loc), 'w') as data_file:
            json.dump(tmp, data_file)

    def remove(self, launcher_profile_loc=join_path(config["minecraft_directory"], "launcher_profiles.json")):
        """
        Removes Profile from launcher_profiles.json
        :param launcher_profile_loc: string, absolute path to the launcher_profiles.json
        :return: None
        """
        with open(launcher_profile_loc) as data_file:
            tmp = json.load(data_file)

        try:
            del tmp["profiles"][self.id.decode()]
        except KeyError:
            pass

        with open(join_path(launcher_profile_loc), 'w') as data_file:
            json.dump(tmp, data_file)

    def __repr__(self):
        return '<Profile id: {}, name: {}, type: {}, created: {}, lastUsed: {}, lastVersionId: {}>'.format(
            self.id,
            self.name,
            self.type,
            self.created,
            self.last_used,
            self.version_id
        )


def rem_profile(id, launcher_profile_loc=join_path(config["minecraft_directory"], "launcher_profiles.json")):
    """
    Removes a Profile from it's id
    :param id: string
    :return: None
    """
    with open(launcher_profile_loc) as data_file:
        tmp = json.load(data_file)

    try:
        del tmp["profiles"][id.decode()]
    except KeyError:
        pass

    with open(join_path(launcher_profile_loc), 'w') as data_file:
        json.dump(tmp, data_file)


def get_profiles():
    """
    Gets all of the profiles which are currently in launcher_profiles.json
    :return: list<dict>
    """
    with open(join_path(config["minecraft_directory"], "launcher_profiles.json")) as p:
        profile_json = json.load(p)["profiles"]

    #pprint.pprint(profile_json)

    profiles = []

    for id, data in profile_json.items():
        #print("{}: {}".format(id, data))
        if id in Collection.query.filter(Collection.mc_id).all():  # if the id is the same as the id of one in our db
            print("{}: {}".format(id, data))
            # it's one of ours:
            profiles.append(
                Profile(
                    id,
                    data["name"],
                    data["lastVersionId"],
                    data["gameDir"],
                    data["type"],
                    data["created"],
                    data["lastUsed"]
                )
            )

    return profiles


class Version:
    def __init__(self, loc):
        self.loc = loc

        self.json_loc = glob.glob(
            join_path(loc, "**.json")
        )[0]
        print(self.json_loc, end="\n\n")
        with open(self.json_loc) as x:
            self.info = json.load(x)

    def id(self):
        return self.info["id"]

    def type(self):
        return self.info["type"]

    def dictify(self):
        """
        Returns a dictionary representing the data in this class
        :return: dict
        """
        return dict(
            id=self.id(),
            type=self.type(),
            loc=self.loc,
            json_loc=self.json_loc
        )

    def __repr__(self):
        return "<Version id: {}, json_loc: \'{}\'>".format(self.id(), self.json_loc)

    def __str__(self):
        return self.json_loc

    def __getitem__(self, item):
        return self.info[item]


def get_versions():
    """
    Gets all of the valid versions, which are currently installed
    :return: list<Version>
    """
    versions = []
    for jsonfile in glob.glob(
            join_path(
                config["minecraft_directory"],
                "versions",
                "*",
                ""
            )
    ):
        versions.append(Version(jsonfile))
    return versions


def get_version_names():
    """
    Gets all of the valid versions, which are currently installed
    :return: list<String>
    """
    versions = []
    for jsonfile in glob.glob(
            join_path(
                config["minecraft_directory"],
                "versions",
                "*",
                "*.json"
            )
    ):
        with open(jsonfile) as x:
            j = json.load(x)
            versions.append(j["id"])

    return versions


if __name__ == "__main__":
    import pprint
    # Testing time!
    pprint.pprint(get_profiles())
    print(get_versions())
