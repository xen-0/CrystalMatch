import cv2
import numpy as np

from config.focus_config import FocusConfig
from dls_util.imaging import Image
from focus.pyramid import pyramid
from os.path import join

from focus.sharpness_detector import SharpnessDetector


class FocusStack:
    CONFIG_FILE_NAME = "focus_stack.ini"

    def __init__(self, images, config_dir):
        self._image_file_list = images
        self._config = FocusConfig(join(config_dir, self.CONFIG_FILE_NAME))

    def composite(self):
        images = self.find_sharp()
        images = np.array(images, dtype=images[0].dtype)

        #TODO:Implement alignment algo
        #aligned_images, gray_images = self.align(images)

        #stacked_image = pyramid(aligned_images, self._config).get_pyramid_fusion()
        stacked_image = pyramid(images, self._config).get_pyramid_fusion()
        stacked_image  = cv2.convertScaleAbs(stacked_image)
        return Image(stacked_image)

    def find_sharp(self):
        images = []
        n = len(self._image_file_list)
        sd = [None]*n
        num = 0
        level = 0

        #calculate fft of every image
        for file_obj in self._image_file_list:
            img_color = cv2.imread(file_obj.name)
            img = cv2.cvtColor(img_color.astype(np.float32), cv2.COLOR_BGR2GRAY)
            #img = img_color
            detector = SharpnessDetector(img)
            detector.runFFT()
            sd[num] = detector
            num = num + 1

        #find the fft cut off
        for i in range(1, n-1):
            if (sd[i+1].getFFT() - sd[i].getFFT())/sd[i].getFFT() > 0.05: #5%
                level = sd [i].getFFT()
                break

        # take all the images which have fft higher than the cut off
        for j in range(1, n):
            if sd[j].getFFT() > level:
                images.append(sd[j].getImage())

        return images
