import os

from test_case import CrystalTestCase


class CrystalTestSuite:
    """ Stores a suite of crystal matching system test data and handles saving/loading from file.
    """
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

    @staticmethod
    def _load_cases_from_file(case_file, image_dir):
        """ Load the test data from the specified csv file. The image directory is prepended to every image
        file given in the test data (This is just to save space in the csv file). """
        cases = []

        with open(case_file) as f:
            lines = f.readlines()

            for line in lines:
                if line.startswith("#") or line.strip() == "":
                    continue

                try:
                    case = CrystalTestSuite._case_from_line(line, image_dir)
                    cases.append(case)
                except ValueError as ex:
                    print("Failed to parse line: '{}'".format(line))

        return cases

    @staticmethod
    def _case_from_line(line, image_dir):
        case = CrystalTestCase.deserialize(line, image_dir)
        return case




