import cv2
import numpy as np

from dls_util.imaging import Image


class FocusStack:
    def __init__(self, images, config):
        self._images = images
        self._config = config

    def composite(self):
        """ Finds the points of best focus in all images and produces a merged result """
        cfg = self._config
        images = self._images

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
