import cv2
import numpy as np
from math import floor, ceil

import pywt

from dls_util.imaging import Image


class FocusStack:
    def __init__(self, images, config):
        self._images = images
        self._config = config

    def calculate_wavelet(self, image_obj, mode='db1', level=10):
        # convert to grayscale
        im_array = image_obj.to_mono().raw()

        # Apply blur
        # blur_size = 3
        # im_array = cv2.GaussianBlur(im_array, (blur_size, blur_size), 0)

        # convert to float
        im_array = np.float32(im_array)
        im_array /= 255
        # compute coefficients
        coeffs = pywt.wavedec2(im_array, mode, level=level)

        # Process Coefficients
        coeffs_H = list(coeffs)
        coeffs_H[0] *= 0

        # reconstruction
        im_array_h = pywt.waverec2(coeffs_H, mode)
        im_array_h = np.absolute(im_array_h)
        # im_array_h *= 255
        # im_array_h = np.uint8(im_array_h)
        # cv2.imshow("wavelet", im_array_h)
        # cv2.waitKey()
        return im_array_h

    def _compute_wavelets(self, images):
        output_array = []
        for img in images:
            output_array.append(self.calculate_wavelet(img))
        return output_array

    def composite(self):
        """ Finds the points of best focus in all images and produces a merged result """
        cfg = self._config
        images = self._images

        kernel_size = cfg.kernel_size.value()
        blur_radius = cfg.blur_radius.value()

        # downscale images
        # original_size = images[0].size()
        # scale = 0.7
        # downscale_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        # for i in range(len(images)):
        #     images[i] = images[i].resize(downscale_size)

        laplacians = self._compute_laplacians(images, kernel_size, blur_radius)

        # wavelets = self._compute_wavelets(images)
        #
        focused_image = self._determine_focused_pixels(images, laplacians)

        # upscale result
        # focused_image = focused_image.resize(original_size)

        return focused_image

    @staticmethod
    def _compute_laplacians(images, kernel_size, blur_size):
        """ Compute the gradient map of the image """

        # TODO: Downscale before Laplacian - upscale final image - will lose detail but also noise
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

        # Making the assumption that the optimum focus level will be in the middle of the stack - merge images
        # on the top and bottom of the stack and work inwards.
        half_len = int(ceil(float(len(laplacians)) / 2.0))
        output = images[0].raw().copy()
        for low_index in range(half_len):
            output = FocusStack._merge_pixels_for_index(low_index, images, laplacians, max_values, output)
            high_index = len(laplacians) - 1 - low_index
            if high_index != low_index:
                output = FocusStack._merge_pixels_for_index(high_index, images, laplacians, max_values, output)

        return Image(output)

    @staticmethod
    def _merge_pixels_for_index(i, images, laplacians, max_values, output):
        mask = laplacians[i] == max_values
        mask = np.resize(mask, (output.shape[0], output.shape[1]))
        mask = np.reshape(np.repeat(mask, 3), output.shape)
        output = np.where(mask, images[i].raw(), output)
        return output
