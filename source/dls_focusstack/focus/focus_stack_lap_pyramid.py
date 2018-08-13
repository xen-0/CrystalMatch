import logging
import logconfig
import time

import cv2
import numpy as np

from dls_focusstack.config.focus_config import FocusConfig
from dls_util.imaging import Image
from dls_focusstack.focus.image_fft_manager import ImageFFTManager
from os.path import join

from dls_focusstack.focus.pyramid_manager import PyramidManager
from dls_focusstack.focus.sharpness_detector import SharpnessDetector


class FocusStack:
    CONFIG_FILE_NAME = "focus_stack.ini"

    def __init__(self, images, config_dir):
        self._image_file_list = images
        self._config = FocusConfig(join(config_dir, self.CONFIG_FILE_NAME))


    def composite(self):
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        log.debug("Starting fft calculation")
        #log.info("t1")

        t1 = time.clock()
        #log.info("t2")
        man = ImageFFTManager(self._image_file_list)
        #log.info("t3")
        man.read_ftt_images()
        #log.info("t9")
        sd = SharpnessDetector(man.get_fft_images(), self._config)

        images = sd.images_to_stack()

        t2 = time.clock() - t1

        #add extra field to the log
        extra = {'FTT_time': t2}
        log = logging.LoggerAdapter(log, extra)
        log.info("FFT calculation finished")
        images = np.array(images, dtype=images[0].dtype)

        #TODO:Implement alignment algo
        #aligned_images, gray_images = self.align(images)

        #stacked_image = pyramid(aligned_images, self._config).get_pyramid_fusion()
        stacked_image = PyramidManager(images, self._config).get_pyramid_fusion()
        #log.info("t17")
        stacked_image  = cv2.convertScaleAbs(stacked_image)
        return Image(stacked_image)





