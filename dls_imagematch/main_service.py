import sys

from os.path import dirname
from sys import path
path.append(dirname(path[0]))


from service import CrystalMatchService

# Detect if the program is running from source or has been bundled
IS_BUNDLED = getattr(sys, 'frozen', False)
if IS_BUNDLED:
    CONFIG_DIR = "./config/"
else:
    CONFIG_DIR = "../config/"


def main():
    dir = "../test-images/Formulatrix/46412/"
    image1_path = dir + "449/A02.jpg"
    image2_path = dir + "584/A02.jpg"

    from dls_util.shape import Point
    selected = [Point(1068, 442), Point(1191, 1415)]

    service = CrystalMatchService(CONFIG_DIR)
    service.perform_match(image1_path, image2_path, selected)


if __name__ == '__main__':
    main()
