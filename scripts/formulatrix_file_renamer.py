import os


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


def get_files_with_dir(dir):
    """ Return a list of all files (full path) in the directory. """
    paths = [os.path.join(dir,o) for o in os.listdir(dir)]
    files = [p for p in paths if os.path.isfile(p)]

    return files


def get_files(dir):
    """ Return a list of all files (full path) in the directory. """
    files = [o for o in os.listdir(dir) if os.path.isfile(os.path.join(dir,o))]

    return files


def name_generator():
    forward = False
    for row in "ABCDEFGH":
        forward ^= True
        cols = range(1, 13) if forward else range(12, 0, -1)
        for col in cols:
            name = str(row) + str(col).zfill(2)
            yield name


TARGET_DIRECTORY = "../test-images/Formulatrix/test"

# Takes a set of directories which each contain an image series from the formulatrix
dir_list = get_sub_dirs(TARGET_DIRECTORY)

# Give files ascending numerical names: 1, 2, 3,... etc
for directory in dir_list:
    # Delete thumbnail files
    files = get_files_with_dir(directory)
    for file in files:
        if file.endswith("th.jpg") or file.endswith("th..jpg"):
            os.remove(file)

    # The folder must contain exactly 96 .jpg files
    files = get_files(directory)
    if len(files) != 96:
        print("Directory {} contains {} files, should be 96. Skipping.".format(directory, len(files)))
        continue
    else:
        bad_extensions = [f[-4:] != ".jpg" for f in files]
        if any(bad_extensions):
            print("Directory {} contains file with '{}' extension, "
                  "should be '.jpg'. Skipping.".format(directory, file[-4:]))
            continue

    # Rename the files
    print("Renaming files in directory {}".format(directory))

    names = name_generator()
    files = sorted(files, key=lambda x: int(x[:-4]))
    for i, file in enumerate(files):
        old_name = directory + "\\" + file
        new_name = directory + "\\" + next(names) + ".jpg"
        os.rename(old_name, new_name)
