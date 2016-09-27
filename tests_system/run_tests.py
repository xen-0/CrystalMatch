from dls_imagematch.service import CrystalMatchService
from test_suite import CrystalTestSuite

config_dir = "../config/"
case_file = "./data/data.csv"
img_dir = "../test-images/Formulatrix/"

suite = CrystalTestSuite(case_file, img_dir)
cases = suite.cases

match_service = CrystalMatchService(config_dir)

for case in cases:
    case.image_1_marked().rescale(0.3).popup()
    case.image_2_marked().rescale(0.3).popup()

    result = match_service.perform_match(case.image_1_path, case.image_2_path, case.image_1_points)

