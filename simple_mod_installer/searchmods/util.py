from simple_mod_installer.database.models import Mod


def match_cursemod_db(cursemod):
    """
    Match a cursemod to it's counterpart in our local database, if any.
    :param cursemod: CurseMod
    :return: list<Mod>, all of the mods we have locally which are from this curse id
    """
    return Mod.query.filter(Mod.curse_id == cursemod.id).all()
