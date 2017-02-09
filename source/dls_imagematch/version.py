# Version information for CrystalMatch
__version__ = "v0.1.5"
__date__ = "09/02/2017"


class VersionHandler:
    def __init__(self):
        pass

    @staticmethod
    def version():
        return __version__

    @staticmethod
    def release_date():
        return __date__

    @staticmethod
    def version_string():
        return '%(prog)s ' + VersionHandler.version() + ', ' + VersionHandler.release_date()
