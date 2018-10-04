"""
Creates the moddata.sqlite database
"""

from simple_mod_installer.database import init_db, db_session
from simple_mod_installer.database.models import *

# create the database
init_db()

# create collection
c = Collection("test", "1.7.10", "Minecraft 1.7.10")
db_session.add(c)
db_session.commit()
