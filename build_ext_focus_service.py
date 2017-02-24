"""
This script creates a distributable directory for the Extended Focus Service.
"""
from os import rmdir, makedirs, listdir, remove
from os.path import exists, isdir, join
from shutil import rmtree, copytree, move, make_archive

DIST_NAME = "ExtendedFocusImageService"
DIST_PARENT_DIR = "./dist/"
ARCHIVE_TYPE = "zip"

dist_dir = join(DIST_PARENT_DIR, DIST_NAME)

# Remove config and log directories from the source files.
print "Cleaning source directory..."
config_dir = "./dls_extended_focus/config"
logs_dir = "./dls_extended_focus/logs"
if exists(config_dir):
    rmtree(config_dir)
if exists(logs_dir):
    rmtree(logs_dir)

# Remove existing resources
print "Deleting existing resources..."
if exists(dist_dir) and isdir(dist_dir):
    rmtree(dist_dir)
makedirs(dist_dir)
remove(dist_dir + "." + ARCHIVE_TYPE)

# Copy Files to distribution directory
print "Copying source files to distribution..."
tmp_dir = join(dist_dir, "temp")
copytree("./dls_extended_focus", tmp_dir)
copytree("./source/dls_util", join(dist_dir, "dls_util"))
for filename in listdir(tmp_dir):
    move(join(tmp_dir, filename), join(dist_dir, filename))
rmdir(tmp_dir)

# Create an archive
print "Creating archive file..."
make_archive(dist_dir, ARCHIVE_TYPE, dist_dir)

print "Done"
print "Distribution available at '" + dist_dir + "." + ARCHIVE_TYPE + "'"
