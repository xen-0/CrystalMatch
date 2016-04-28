import os

class File:
    @staticmethod
    def get_sub_dirs(dir, startswith="", endswith=""):
        """ Return the full path of all immediate subdirectories in the
        specified directory. """
        dirs = os.listdir(dir)

        if startswith != "":
            dirs = [d for d in dirs if d.startswith(startswith)]

        if endswith != "":
            dirs = [d for d in dirs if d.endswith(endswith)]

        paths = [os.path.join(dir, d) for d in dirs]
        sub_dirs = [p for p in paths if os.path.isdir(p)]
        return sub_dirs

    @staticmethod
    def get_files(dir, extensions=[]):
        """ Return a list of all files (full path) in the directory. Can be
        restricted to specific extensions. """
        paths = [os.path.join(dir,o) for o in os.listdir(dir)]
        files = [p for p in paths if os.path.isfile(p)]

        if len(extensions) > 0:
            files = [f for f in files if os.path.splitext(f)[1][1:] in extensions]

        return files