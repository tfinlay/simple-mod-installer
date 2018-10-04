from sqlalchemy import Column, Integer, String, Table, ForeignKey, PrimaryKeyConstraint, Binary, UnicodeText, VARCHAR
from sqlalchemy.orm import relationship, backref, relation, mapper
from simple_mod_installer.database import Base
import time
from hashlib import sha256
from simple_mod_installer import config, util


mod_collection_relationship_table = Table(
    'mod_collection_relationship_table',
    Base.metadata,
    Column('mod_id', Integer, ForeignKey('mods.id'), nullable=False),
    Column('collection_id', Integer, ForeignKey('collections.id'), nullable=False),
    PrimaryKeyConstraint('mod_id', 'collection_id')  # there can only be one pair of the same mod_id and collection_id
)

"""
class ModModDependencyRelationship(Base):
    __tablename__ = 'mod_mod_dependency_relationship'
    mod_1_id = Column(Integer, ForeignKey('mods.id'), nullable=False, primary_key=True)
    mod_2_id = Column(Integer, ForeignKey('mods.id'), nullable=False, primary_key=True)
"""
"""
mod_mod_dependency_table = Table(
    'mod_mod_dependency_table',
    Base.metadata,
    Column('dependant', Integer, ForeignKey('mods.id'), nullable=False, primary_key=True),
    Column('dependency', String, nullable=False, primary_key=True),
    PrimaryKeyConstraint('dependant', 'dependency')  # there can only be one pair of the same mod_id and dependency
)
"""

mod_dependency_table = Table(
    'mod_dependency_table',
    Base.metadata,
    Column('dependant', Integer, ForeignKey('mods.id'), nullable=False, primary_key=True),
    Column('dependency', String, ForeignKey('depmods.id'), nullable=False, primary_key=True),
    PrimaryKeyConstraint('dependant', 'dependency')  # this mod can only have one dependency that's the same
)


class DepMod(Base):
    """
    A Dependency Mod, a placeholder for a dependency
    """
    __tablename__ = 'depmods'
    id = Column(Integer, primary_key=True)
    modid = Column(String, nullable=False)

    def __init__(self, modid):
        self.modid = modid

    def __repr__(self):
        return '<DepMod (id: {}, modid: {!r})>'.format(self.id, self.modid)


class Mod(Base):
    __tablename__ = 'mods'
    id = Column(Integer, primary_key=True)
    filename = Column(String(120), nullable=False)

    # MCMod.info metadata
    name = Column(String(120), nullable=True)
    modid = Column(String(120), nullable=True)
    version = Column(String(12), nullable=True)
    mc_version = Column(String(10), nullable=True)
    update_json_url = Column(String(255), nullable=True)  # See: http://mcforge.readthedocs.io/en/latest/gettingstarted/autoupdate/#forge-update-checker
    description = Column(UnicodeText, nullable=True)
    credits = Column(UnicodeText, nullable=True)

    authors = relationship('ModAuthor')

    download_url = Column(String(255), nullable=True)  # if it's been downloaded via direct download, store the URL here

    # Curse data
    curse_id = Column(String(9), nullable=True)
    curse_file_id = Column(String(9), nullable=True)

    # Provider metadata
    # TO BE ADDED. Metadata about e.g. Curse id etc. for updating and additional metadata

    #dependencies = relationship('Mod', secondary=mod_mod_dependency_table, backref=backref("Mod", order_by=id), foreign_keys=[id])  # link to other mods as dependencies
    """
    dependencies = relation(
        'Mod',
        secondary=mod_mod_dependency_table,
        primaryjoin=mod_mod_dependency_table.c.dependant == id,
        secondaryjoin=mod_mod_dependency_table.c.dependency == id,
        backref=backref('m')
    )
    """
    dependencies = relation(
        'DepMod',
        secondary=mod_dependency_table,
        backref=backref('mods')
    )

    def __init__(self, filename, name=None, modid=None, version=None, mc_version=None, update_json_url=None, description=None, creds=None, dl_url=None, dependencies=(), curse_id=None, curse_file_id=None, authors=()):
        self.filename = filename
        self.name = name
        self.modid = modid
        self.version = version
        self.mc_version = mc_version
        self.update_json_url = update_json_url
        self.description = description
        self.credits = creds
        self.download_url = dl_url
        self.authors.extend(authors)

        self.curse_id = curse_id
        self.curse_file_id = curse_file_id

        print(dependencies)
        for dep in dependencies:
            pass
            self.add_dependency(dep)

    def add_dependency(self, depmod):
        """
        Makes this mod dependant on a mod with modid
        :param depmod: String
        :return: None
        """
        print("Adding {!r} as dependency for {!r}".format(depmod, self))

        self.dependencies.append(depmod)

    def rem_dependency(self, modid):
        """
        Removes this mod's dependency on a mod with modid
        :param modid: String
        :return: None
        """
        self.dependencies.remove(modid)

    def __repr__(self):
        return '<Mod id:{!r}, filename: {!r}, modid: {!r}>'.format(self.id, self.filename, self.modid)


class ModAuthor(Base):
    __tablename__ = 'modauthors'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    parent_id = Column(Integer, ForeignKey('mods.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<ModAuthor id: {!r}, name: {!r}>'.format(self.id, self.name)

    def __str__(self):
        return str(self.name)


class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)      # the ID number of the Collection. Also the name of the directory containing it and the computer-name of the profile
    mc_id = Column(Binary(32), nullable=False)  # the ID of the Collection, as specified in the launcher_profiles.json. It's a sha256 hash of the original name.
    name = Column(String(120), nullable=False)  # user-defined: the name of the Collection. Used as profile name in launcher_profiles.json
    mc_version = Column(String(10), nullable=False)  # auto-filled (user modifiable): from either id of version json, or assets. Depending if selected version_id is Vanilla or Forge / other
    version_id = Column(String(100), nullable=False)  # user-selected: the id of the minecraft verison to run (for use in launcher_profiles.json as "lastVersionId")
    epoch_created = Column(Integer, nullable=False)  # auto-filled: the epoch-format time of creation. To be converted to YYYY-MM-DDTHH:MM:SS:mmmm for launcher_profiles.json (under "created")
    mods = relationship('Mod', secondary=mod_collection_relationship_table, backref=backref("collections"))

    def __init__(self, name, mc_version, version_id):
        self.name = name
        self.mc_id = sha256(name.encode()).hexdigest().encode()
        self.mc_version = mc_version
        self.version_id = version_id
        self.epoch_created = int(time.time())

    def get_collection_path(self):
        """
        Returns an absolute path to the collection's directory
        :return: string
        """
        return util.join_path(
            config["application_root"],
            "collections",
            self.mc_id.decode()
        )

    def add_mod(self, mod):
        self.mods.append(mod)

    def rem_mod(self, mod):
        self.mods.remove(mod)

    def __repr__(self):
        return '<Collection id: {!r}, name: {!r}>'.format(self.id, self.name)
