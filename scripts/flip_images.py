import cv2
from os import listdir

from os.path import join, isfile

###########################################################
# SETTINGS
DIR_NAME = "C:\\Users\\marcs\\Documents\\Diamond Light Source\\VMXi\\Data\\test-images\\Beamline\\52365\\20170104\\VMXI_Image_ZStack_2"
EXTENSIONS = ['jpg', 'png']
FLIP_VERTICAL = True
FLIP_HORIZONTAL = False
###########################################################

file_list = listdir(DIR_NAME)
image_files = [join(DIR_NAME, fn) for fn in file_list if any(fn.lower().endswith(ext) for ext in EXTENSIONS) and isfile(join(DIR_NAME, fn))]

for path in image_files:
    print "Flipping '" + path + "'"
    img = cv2.imread(path)
    if FLIP_VERTICAL:
        img = cv2.flip(img, 0)
    if FLIP_HORIZONTAL:
        img = cv2.flip(img, 1)
    cv2.imwrite(path, img)
print "Done!"
