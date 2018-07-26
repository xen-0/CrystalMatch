import logging
import time
from multiprocessing import Process, Queue, current_process, Pool

import cv2
import numpy as np

from config.focus_config import FocusConfig
from dls_util.imaging import Image
from focus.image_fft_manager import ImageFFTManager
from os.path import join

from focus.pyramid_manager import PyramidManager
from focus.sharpness_detector import SharpnessDetector


class FocusStack:
    CONFIG_FILE_NAME = "focus_stack.ini"

    def __init__(self, images, config_dir):
        self._image_file_list = images
        self._config = FocusConfig(join(config_dir, self.CONFIG_FILE_NAME))

    def composite(self):
        t1 = time.clock()
        man = ImageFFTManager(self._image_file_list)
        man.read_ftt_images()
        sd = SharpnessDetector(man.get_fft_images())

        images = sd.images_to_stack()

        t2 = time.clock() - t1
        logger = logging.getLogger(__name__)
        logger.debug("FFT calculation time, " + str(t2))
        images = np.array(images, dtype=images[0].dtype)

        #TODO:Implement alignment algo
        #aligned_images, gray_images = self.align(images)

        #stacked_image = pyramid(aligned_images, self._config).get_pyramid_fusion()
        stacked_image = PyramidManager(images, self._config).get_pyramid_fusion()
        stacked_image  = cv2.convertScaleAbs(stacked_image)
        return Image(stacked_image)





