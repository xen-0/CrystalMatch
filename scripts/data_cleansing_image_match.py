# Uses the alignment stage of the CrystalMatch algorithm to compare images in two directories and attempt to rename
# images in the second directory which do not match their counterparts in the main directory. Any images for which a
# match cannot be found at the end of the process will be left in the 'unmatched' directory created in each target
# directory.
from os import listdir, makedirs, rename
from os.path import join, exists, isdir
from dls_imagematch.service.service import CrystalMatchService

# CONFIGURATION
######################################################################
MAIN_DIR = "../test-images/Formulatrix/46532/545"
TARGET_DIR_LIST = [
    # "../test-images/Formulatrix/46532/548",
    # "../test-images/Formulatrix/46532/551",
    # "../test-images/Formulatrix/46532/554",
    # "../test-images/Formulatrix/46532/557",
    # "../test-images/Formulatrix/46532/560",
    # "../test-images/Formulatrix/46532/563",
    # "../test-images/Formulatrix/46532/629",
    # "../test-images/Formulatrix/46532/635",
    "../test-images/Formulatrix/46532/644",
]
CONFIG_DIR = "../config"
UNMATCHED_DIR_NAME = "unmatched"
ACCEPTABLE_ERROR_THRESHOLD = 13
######################################################################


def validate_image_file(file_name):
    return file_name.endswith(".jpg") or file_name.endswith(".tif")


def get_unmatched_dir(parent_dir):
    unmatched_dir = join(parent_dir, UNMATCHED_DIR_NAME)
    if not exists(unmatched_dir) or not isdir(unmatched_dir):
        makedirs(unmatched_dir)
    return unmatched_dir


def move_to_unmatched(parent_dir, file_name):
    unmatched_dir = get_unmatched_dir(parent_dir)
    print 'Moving "' + file_name + '" to unmatched'
    rename(join(parent_dir, file_name), join(unmatched_dir, file_name))


def move_matched_files(parent_dir_1, parent_dir_2, true_file_name, replaced_file_name):
    unmatched_dir = get_unmatched_dir(parent_dir_1)
    rename(join(unmatched_dir, true_file_name), join(parent_dir_1, true_file_name))
    unmatched_dir = get_unmatched_dir(parent_dir_2)
    rename(join(unmatched_dir, replaced_file_name), join(parent_dir_2, true_file_name))


def compare_image_directories(target_dir):
    dir_list_1 = listdir(MAIN_DIR)
    dir_list_2 = listdir(target_dir)
    alignment_service = CrystalMatchService(CONFIG_DIR)
    for image_name in dir_list_1:
        # Skip non-image files
        if not validate_image_file(image_name):
            print "Skipping in src dir: " + image_name
            continue
        # Check matching image names first
        if image_name in dir_list_2:
            dir_list_2.remove(image_name)
            image_1 = join(MAIN_DIR, image_name)
            image_2 = join(target_dir, image_name)
            results = alignment_service.perform_match(image_1, image_2, [])
            # noinspection PyProtectedMember
            if results._alignment_status_code.code != 1:
                move_to_unmatched(MAIN_DIR, image_name)
                move_to_unmatched(target_dir, image_name)
        else:
            # Move to unmatched for the second pass
            move_to_unmatched(MAIN_DIR, image_name)
    for unmatched_file in dir_list_2:
        if not validate_image_file(unmatched_file):
            print "Skipping in dst dir: " + unmatched_file
            continue
        move_to_unmatched(target_dir, unmatched_file)

    # Second Pass - iterate over each image in unmatched attempting to find a match.
    unmatched_list_1 = listdir(get_unmatched_dir(MAIN_DIR))
    unmatched_list_2 = listdir(get_unmatched_dir(target_dir))
    for unmatched_img_name in unmatched_list_1:
        index = 0
        target_image = join(get_unmatched_dir(MAIN_DIR), unmatched_img_name)
        err_val = 0
        while index < len(unmatched_list_2):
            potential_img_name = unmatched_list_2[index]
            candidate_image = join(get_unmatched_dir(target_dir), potential_img_name)
            results = alignment_service.perform_match(target_image, candidate_image, [])
            # noinspection PyProtectedMember
            err_val = results._alignment_error
            if err_val < ACCEPTABLE_ERROR_THRESHOLD:
                break
            index += 1
        if index < len(unmatched_list_2):
            print 'Match found "' + unmatched_img_name + '" -> "' + potential_img_name + \
                  '" (err: ' + str(err_val) + ')'
            move_matched_files(MAIN_DIR, target_dir, unmatched_img_name, potential_img_name)
            unmatched_list_2.remove(potential_img_name)
        else:
            print 'No match found for "' + unmatched_img_name + '"'

    # Finally restore images in the main unmatched directory as they may be required for next comparison
    print "Relocating files from '" + get_unmatched_dir(MAIN_DIR) + "'..."
    for file_name in listdir(get_unmatched_dir(MAIN_DIR)):
        rename(join(get_unmatched_dir(MAIN_DIR), file_name), join(MAIN_DIR, file_name))

for dir_path in TARGET_DIR_LIST:
    print "Starting directory '" + dir_path + "'..."
    compare_image_directories(dir_path)
    print "Done!\n\n"
