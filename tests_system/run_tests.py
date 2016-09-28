from dls_imagematch.service import CrystalMatchService
from test_suite import CrystalTestSuite

config_dir = "../config/"
case_file = "./data/cases_blank.csv"
img_dir = "../test-images/Formulatrix/"

suite = CrystalTestSuite(case_file, img_dir)
cases = suite.testable_cases()

match_service = CrystalMatchService(config_dir)

print("Number of testable cases: {}".format(len(cases)))

for i, case in enumerate(cases):
    print("\n\n{}   TEST CASE {}   {}".format("+"*20, i+1, "+"*50))
    case.image_marked(1).rescale(0.3).popup(block=False)

    result = match_service.perform_match(case.image_path(1), case.image_path(2), case.image_points(1))

