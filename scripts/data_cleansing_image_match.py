# Uses the alignment stage of the CrystalMatch algorithm to compare images in two directories and attempt to rename
# images in the second directory which do not match their counterparts in the main directory. Renamed images are moved
# to a new directory called 'matched' at the root of the second directory, if multiple matches are found a directory
# is created to contain all the possible matches.  To help fix these conflicts a CSV file will be created for each
# file which lists the error value for each match found for a specified image.
# NOTE: The restructured files record the process of the script - it can therefore be stopped and restarted at will.
import csv
from multiprocessing import Pool
from os import listdir, makedirs, rename
from os.path import join, exists, isdir, splitext
from dls_imagematch.service.service import CrystalMatchService

# CONFIGURATION
######################################################################
TARGET_DIR_LIST = [
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/548"],
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/551"],
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/554"],
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/557"],
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/560"],
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/563"],
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/629"],
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/635"],
    ["../test-images/Formulatrix/46532/545", "../test-images/Formulatrix/46532/644"],

    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/452"],
    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/455"],
    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/458"],
    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/461"],
    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/464"],
    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/527"],
    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/533"],
    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/581"],
    ["../test-images/Formulatrix/46412/449", "../test-images/Formulatrix/46412/584"],
]

CONFIG_DIR = "../config"
UNMATCHED_DIR_NAME = "unmatched"
PARALLEL_PROCESSES = None  # Set to None to create one process for each core
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


# noinspection PyProtectedMember
def run_match(bundle):
    candidate_name, target_image, candidate_image = bundle
    service = CrystalMatchService(CONFIG_DIR)
    result = service.perform_match(target_image, candidate_image, [])
    return candidate_name, result._alignment_status_code.code, result._alignment_error


# noinspection PyProtectedMember
def exhaustive_compare_image_directories(main_dir, target_dir):
    main_dir_list = []
    target_dir_list = []

    # Get file lists
    for file_name in listdir(main_dir):
        if validate_image_file(file_name):
            main_dir_list.append(file_name)
    for file_name in listdir(target_dir):
        if validate_image_file(file_name):
            target_dir_list.append(file_name)

    # Ensure the matched directory exists
    cpy_dir = join(target_dir, "matched")
    if not exists(cpy_dir):
        makedirs(cpy_dir)

    # Compare lists
    for target_img_name in target_dir_list:
        jobs = []
        for orig_img_name in main_dir_list:
            jobs.append((orig_img_name, join(target_dir, target_img_name), join(main_dir, orig_img_name)))

        # Set up a worker pool for this job set
        worker_pool = Pool(PARALLEL_PROCESSES)
        results = worker_pool.imap(run_match, jobs)
        worker_pool.close()
        worker_pool.join()

        # interpret the results.
        csv_data = []
        for i in range(results._length):
            candidate_name, state_code, error_value = results.next()
            if state_code == 1:
                csv_data.append([candidate_name, error_value])
        if len(csv_data) > 0:
            csv_data = sorted(csv_data, key=lambda x: x[1])
            best_match = csv_data[0][0]
            old_file_path = join(target_dir, target_img_name)
            new_img_path = join(cpy_dir, best_match)
            new_img_dir = splitext(new_img_path)[0]
            if exists(new_img_path):
                # Create a dir and copy both matches into it - add a suffix to each file name
                makedirs(new_img_dir)
                # Move existing files
                existing_file = get_unique_filename(new_img_dir, best_match)
                rename(new_img_path, existing_file)
                existing_csv_file = splitext(new_img_path)[0] + '.csv'
                if exists(existing_csv_file):
                    rename(existing_csv_file, splitext(existing_file)[0] + '.csv')
                # Place new file
                new_image_path = get_unique_filename(new_img_dir, best_match)
                rename(old_file_path, new_image_path)
            elif exists(new_img_dir) and isdir(new_img_dir):
                # Copy the image to the directory with a suffix
                new_image_path = get_unique_filename(new_img_dir, best_match)
                rename(old_file_path, new_image_path)
            else:
                # Copy the image to the matched directory.
                new_image_path = join(cpy_dir, best_match)
                rename(old_file_path, new_image_path)
            # Create the csv file alongside the moved file.
            write_csv_file_for_matches(new_image_path, csv_data)
        else:
            print "No match found: '" + target_img_name + "'"


def write_csv_file_for_matches(image_file_path, csv_data):
    image_file_path = splitext(image_file_path)[0] + '.csv'
    with open(image_file_path, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)


def get_unique_filename(directory, filename):
    i = 0
    split_path = splitext(join(directory, filename))
    while exists(split_path[0] + "_" + str(i) + split_path[1]):
        i += 1
    img_dir_path = split_path[0] + "_" + str(i) + split_path[1]
    return img_dir_path


if __name__ == '__main__':
    for dir_path in TARGET_DIR_LIST:
        print "Comparing directory '" + dir_path[0] + "' to '" + dir_path[1] + "'..."
        exhaustive_compare_image_directories(dir_path[0], dir_path[1])
        print "Done!\n\n"
