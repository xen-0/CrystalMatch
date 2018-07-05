"""
Create a new dataset JSON file by filtering results form another dataset.
Filtering is carried out by a REGEX applied to the image paths.
"""
from test_suite import CrystalTestSuite


copy_from = "../data-sets/GDA_2018_07_04.json"
copy_to = "../data-sets/VMXi-AB0634.json"
regex_string = ".*VMXi-AB0634.*"

# Load the test suite and copy to another dataset
original_test_suite = CrystalTestSuite(copy_from, "/")
new_test_suite = CrystalTestSuite(copy_to, "/")
original_test_suite.filter_by_path_match(new_test_suite, regex_string)

new_test_suite.save_to_file()
