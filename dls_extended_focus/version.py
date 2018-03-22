# Version information for Extended Focus Service
__version__ = "v0.0.3"
__date__ = "30/03/2017"


class VersionHandler:
    def __init__(self):
        pass

    @staticmethod
    def version():
        return __version__

    @staticmethod
    def release_date():
        return __date__
