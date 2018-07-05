"""
Create a new dataset JSON file by filtering results form another dataset.
Filtering is carried out by a REGEX applied to the image paths.
"""
from test_suite import CrystalTestSuite


copy_from = "../data-sets/GDA_master_2018_04_18.json"
copy_to = "../data-sets/mitegen-pre-2018-04-18.json"
regex_string = ".*VMXi-AB(0094|0095|0148|0168|0192|0193|0275|0276|0377|0446|0447|0448).*"

# Load the test suite and copy to another dataset
original_test_suite = CrystalTestSuite(copy_from, "/")
new_test_suite = CrystalTestSuite(copy_to, "/")
original_test_suite.filter_by_path_match(new_test_suite, regex_string)

new_test_suite.save_to_file()
