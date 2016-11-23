# Run on two image directories
from os import listdir, makedirs, rename
from os.path import join, exists, isdir
from dls_imagematch.service.service import CrystalMatchService

# CONFIGURATION
######################################################################
TARGET_DIR_1 = "../test-images/Formulatrix/46412/449"
TARGET_DIR_2 = "../test-images/Formulatrix/46412/584"
CONFIG_DIR = "../config"
UNMATCHED_DIR_NAME = "unmatched"
######################################################################


def validate_image_file(file_name):
    return file_name.endswith(".jpg") or file_name.endswith(".tif")


def get_unmatched_dir(parent_dir):
    unmatched_dir = join(parent_dir, UNMATCHED_DIR_NAME)
    if not exists(unmatched_dir) or not isdir(unmatched_dir):
        makedirs(unmatched_dir)
    return unmatched_dir

dir_list_1 = listdir(TARGET_DIR_1)
dir_list_2 = listdir(TARGET_DIR_2)
alignment_service = CrystalMatchService(CONFIG_DIR)


def move_to_unmatched(parent_dir, file_name):
    unmatched_dir = get_unmatched_dir(parent_dir)
    print 'Moving "' + file_name + '" to unmatched'
    rename(join(parent_dir, file_name), join(unmatched_dir, file_name))


def move_matched_files(parent_dir_1, parent_dir_2, true_file_name, replaced_file_name):
    unmatched_dir = get_unmatched_dir(parent_dir_1)
    rename(join(unmatched_dir, true_file_name), join(parent_dir_1, true_file_name))
    unmatched_dir = get_unmatched_dir(parent_dir_2)
    rename(join(unmatched_dir, replaced_file_name), join(parent_dir_2, true_file_name))


for image_name in dir_list_1:
    # Skip non-image files
    if not validate_image_file(image_name):
        print "Skipping in src dir: " + image_name
        continue
    # Check matching image names first
    if image_name in dir_list_2:
        dir_list_2.remove(image_name)
        image_1 = join(TARGET_DIR_1, image_name)
        image_2 = join(TARGET_DIR_2, image_name)
        results = alignment_service.perform_match(image_1, image_2, [])
        # noinspection PyProtectedMember
        if results._alignment_status_code.code != 1:
            move_to_unmatched(TARGET_DIR_1, image_name)
            move_to_unmatched(TARGET_DIR_2, image_name)
    else:
        # Move to unmatched for the second pass
        move_to_unmatched(TARGET_DIR_1, image_name)

for unmatched_file in dir_list_2:
    if not validate_image_file(unmatched_file):
        print "Skipping in dst dir: " + unmatched_file
        continue
    move_to_unmatched(TARGET_DIR_2, unmatched_file)

# Second Pass - iterate over each image in unmatched attempting to find a match.
unmatched_list_1 = listdir(get_unmatched_dir(TARGET_DIR_1))
unmatched_list_2 = listdir(get_unmatched_dir(TARGET_DIR_2))

for unmatched_img_name in unmatched_list_1:
    index = 0
    target_image = join(get_unmatched_dir(TARGET_DIR_1), unmatched_img_name)
    while index < len(unmatched_list_2):
        potential_img_name = unmatched_list_2[index]
        candidate_image = join(get_unmatched_dir(TARGET_DIR_2), potential_img_name)
        results = alignment_service.perform_match(target_image, candidate_image, [])
        # noinspection PyProtectedMember
        if results._alignment_status_code.code == 1:
            break
        index += 1
    if index < len(unmatched_list_2):
        print 'Match found "' + unmatched_img_name + '" -> "' + potential_img_name + '"'
        move_matched_files(TARGET_DIR_1, TARGET_DIR_2, unmatched_img_name, potential_img_name)
        unmatched_list_2.remove(potential_img_name)
    else:
        print 'No match found for "' + unmatched_img_name + '"'
