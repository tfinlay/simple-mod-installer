class Error(Exception):
    pass


class CollectionExistsError(Error):
    """
    Exception raised when a Collection already exists, and an attempt to create one has been made.
    """
    def __init__(self, id=None):
        """
        :param id: string, the id of the Collection which holds this name.
        """
        self.id = id


class CollectionNotExistError(Error):
    """
    Exception raised when a Collection doesn't exist and an attempt has been made to get it.
    """
    def __init__(self, id=None):
        """
        :param id: string, the id of the Collection which an attempt was made to find.
        """
        self.id = id


class ModExistsError(Error):
    """
    Exception raised when a Mod already exists and an attempt has been made to add it again.
    """
    def __init__(self, id):
        """
        :param id: string, the id of the Mod which already exists
        """
        self.id = id

class ModNotExistError(Error):
    """
    Exception raised when a Mod doesn't exist and an attempt has been made to get it.
    """
    def __init__(self, id=None):
        """
        :param id: string, the id of the Mod which an attempt was made to find.
        """
        self.id = id

class ModInfoNotExistError(Error):
    """
    Exception raised when a Mod has an mcmod.info file which is impossible to read/
    """