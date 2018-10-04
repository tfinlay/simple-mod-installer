from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from simple_mod_installer import config
import sys
import inspect
#from simple_mod_installer.util import make_path as mp

uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])

#path_to_db = mp(
#    'sqlite:////{}'.format(
#        uppath(os.path.abspath(inspect.stack()[0][1]), 3)  # up three depths from the location of this file (database/__init__.py)
#    ),
#    'moddata.db'
#)

path_to_db = "sqlite:///../moddata.sqlite"

#path_to_db = "sqlite:////{}".format(os.path.join(config["application_root"], "moddata.sqlite"))

print(repr(path_to_db))

engine = create_engine(
    path_to_db,
    convert_unicode=True)
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import simple_mod_installer.database.models
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("database initialised!")
    #from simple_mod_installer.database.models import Collection
    #c = Collection("test", "1.7.10", "Minecraft 1.7.10")
    #db_session.add(c)
    #db_session.commit()
