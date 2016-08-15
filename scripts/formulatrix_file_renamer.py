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


TARGET_DIRECTORY = "."

forward = False
for row in "ABCDEFGH":
    forward ^= True
    cols = range(1, 13) if forward else range(12, 0, -1)
    for col in cols:
        name = str(row) + str(col).zfill(2)
        print(name)
    
# # Takes a set of directories which each contain an image series from the formulatrix
# dir_list = get_sub_dirs(TARGET_DIRECTORY)
#
# # Give files ascending numerical names: 1, 2, 3,... etc
# for dir in dir_list:
#     # Delete thumbnail files
#     files = get_files_with_dir(dir)
#     for file in files:
#         if file.endswith("th.jpg") or file.endswith("th..jpg"):
#             os.remove(file)
#
#     # If the folder doesn't contain 96 files, skip it
#     files = get_files(dir)
#     if len(files) != 96:
#         print("Directory {} contains {} files, should be 96. Skipping.".format(dir, len(files)))
#         continue
#
#     files = sorted(files, key=lambda x: int(x[:-4]))
#     for i, file in enumerate(files):
#         old_name = dir + "\\" + file
#         new_name = dir + "\\" + str(i+1).zfill(2) + ".jpg"
#         os.rename(old_name, new_name)
#
#     forward = False
#     for row in "ABCDEFGH":
#         forward ^= True
#         cols = range(1, 13) if forward else range(12, 1, -1)
#         for col in cols:
#             name = str(row) + str(col).zfill(2)
#             print(name)
