import json
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
        self._scale_ratio = (1.0, 1.0)
        self.cases = self._load_cases_from_file(case_file, image_directory)

    def testable_cases(self):
        return [c for c in self.cases if c.is_testable_case()]

    def image_directory(self): return self._image_directory

    def scale_ratio(self): return self._scale_ratio

    def set_scale_ratio(self, sr1, sr2): self._scale_ratio = (sr1, sr2)

    def calculate_scale(self): return self._scale_ratio[1] / self._scale_ratio[0]

    def save_to_file(self):
        output = {
            "dataset": {
                "relative_scale": {
                    "formulatrix": self._scale_ratio[0], "beamline": self._scale_ratio[1]
                },
                "test_cases": []
            }}

        for case in self.cases:
            output["dataset"]["test_cases"].append(case.serialize())
        with open(self._case_file, 'w') as f:
            json.dump(output, f)

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

    def _load_cases_from_file(self, case_file, image_dir):
        """ Load the test data from the specified csv file. The image directory is prepended to every image
        file given in the test data (This is just to save space in the csv file). """
        cases = []
        try:
            with open(case_file) as f:
                json_data = json.load(f)
            dataset = json_data["dataset"]

            # Load scale ratio
            self.set_scale_ratio(dataset["relative_scale"]["formulatrix"], dataset["relative_scale"]["beamline"])

            # Load test cases
            for test_case in dataset["test_cases"]:
                cases.append(CrystalTestCase.deserialize(test_case, image_dir))
        except IOError:
            # This is not necessarily a problem - this could be a new Test Suite
            print "WARNING: Data set file does not exist."

        return cases
