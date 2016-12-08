import os

from os import listdir

from os.path import splitext, join, relpath

from test_case import CrystalTestCase


class CrystalTestSuite:
    """ Stores a suite of crystal matching system test data and handles saving/loading from file.
    """
    ACCEPTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".tif"]

    def __init__(self, case_file, image_directory):
        self._case_file = case_file
        self._image_directory = image_directory

        self.cases = self._load_cases_from_file(case_file, image_directory)

    def testable_cases(self):
        return [c for c in self.cases if c.is_testable_case()]

    def image_directory(self): return self._image_directory

    def save_to_file(self):
        if not os.path.exists(os.path.dirname(self._case_file)):
            os.makedirs(os.path.dirname(self._case_file))

        with open(self._case_file, 'w') as f:
            for case in self.cases:
                f.write(case.serialize() + "\n")

    def create_cases_from_files(self, dir_1, dir_2):
        """ Compare two directories and create a new case for every image file with the same name. """
        file_list_1 = listdir(dir_1)
        file_list_2 = listdir(dir_2)
        candidate_list = [x for x in file_list_1 if self._has_image_extension(x)]
        for file_name in candidate_list:
            if file_name in file_list_2:
                img_1 = relpath(join(dir_1, file_name), self._image_directory)
                img_2 = relpath(join(dir_2, file_name), self._image_directory)
                self.cases.append(CrystalTestCase.create_new(self._image_directory, img_1, img_2))

    def _has_image_extension(self, file_name):
        path, ext = splitext(file_name)
        return ext in self.ACCEPTED_IMAGE_FORMATS

    @staticmethod
    def _load_cases_from_file(case_file, image_dir):
        """ Load the test data from the specified csv file. The image directory is prepended to every image
        file given in the test data (This is just to save space in the csv file). """
        cases = []

        try:
            with open(case_file) as f:
                lines = f.readlines()

                for line in lines:
                    if line.startswith("#") or line.strip() == "":
                        continue

                    try:
                        case = CrystalTestSuite._case_from_line(line, image_dir)
                        cases.append(case)
                    except ValueError:
                        print("Failed to parse line: '{}'".format(line))
        except IOError:
            # This is not necessarily a problem - this could be a new Test Suite
            print "WARNING: Data set file does not exist."

        return cases

    @staticmethod
    def _case_from_line(line, image_dir):
        case = CrystalTestCase.deserialize(line, image_dir)
        return case
