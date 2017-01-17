import cv2
import numpy as np
from os.path import join

from config.focus_config import FocusConfig
from dls_util.imaging import Image


class FocusStack:
    CONFIG_FILE_NAME = "focus_stack.ini"

    def __init__(self, image_file_list, config_dir):
        self._image_file_list = image_file_list
        self._config = FocusConfig(join(config_dir, self.CONFIG_FILE_NAME))

    def composite(self):
        """ Finds the points of best focus in all images and produces a merged result """
        cfg = self._config

        # Convert images to util Image class
        images = []
        for file_obj in self._image_file_list:
            images.append(Image.from_file(file_obj.name))

        kernel_size = cfg.kernel_size.value()
        blur_radius = cfg.blur_radius.value()
        laplacians = self._compute_laplacians(images, kernel_size, blur_radius)

        focused_image = self._determine_focused_pixels(images, laplacians)

        return focused_image

    @staticmethod
    def _compute_laplacians(images, kernel_size, blur_size):
        """ Compute the gradient map of the image """

        print("Computing the laplacian of the blurred images")
        laps = []
        for i in range(len(images)):
            print "Lap {}".format(i)
            image = images[i].to_mono().raw()
            blurred = cv2.GaussianBlur(image, (blur_size, blur_size), 0)
            result = cv2.Laplacian(blurred, cv2.CV_64F, ksize=kernel_size)
            laps.append(result)

        laps = np.asarray(laps)
        print "Shape of array of laplacians = {}".format(laps.shape)

        return laps

    @staticmethod
    def _determine_focused_pixels(images, laplacians):

        max_values = laplacians[0].copy()
        for i in range(1, len(laplacians)):
            max_values = np.maximum(max_values, laplacians[i])

        output = images[0].raw().copy()
        for i in range(len(laplacians)):
            mask = laplacians[i] == max_values
            mask = np.reshape(np.repeat(mask, 3), output.shape)
            output = np.where(mask, images[i].raw(), output)

        return Image(output)
