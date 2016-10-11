import cv2
import numpy as np

from dls_imagematch.feature import FeatureMatcher
from dls_util.imaging import Image


class FocusStack:
    def __init__(self, images, config):
        self._images = images
        self._config = config

    def composite(self, with_align=True):
        """ Finds the points of best focus in all images and produces a merged result """
        cfg = self._config

        if with_align:
            method = cfg.align_method.value()
            out_dir = cfg.output_dir.value()
            images = self._align_images(self._images, method, out_dir)
        else:
            images = self._images

        kernel_size = cfg.kernel_size.value()
        blur_radius = cfg.blur_radius.value()
        laplacians = self._compute_laplacians(images, kernel_size, blur_radius)

        focused_image = self._determine_focused_pixels(images, laplacians)

        return focused_image

    @staticmethod
    def _align_images(images, method, out_dir):
        aligned_images = []

        # TODO - Frame-by-frame alignment where each frame is aligned with the previous one. This will mean
        # TODO - that the transform for a frame needs to be the product of all transforms that proceeded it

        image1 = images[0]
        for i in range(1, len(images)):
            print("Aligning image {}/{}".format(i+1, len(images)))
            #image1 = images[i-1]
            image2 = images[i]
            matcher = FeatureMatcher(image1, image2)
            matcher.set_detector(method)

            transform = matcher.match()
            transformed_image = transform.inverse_transform_image(image2, image2.size())
            transformed_image.save("{}aligned{}.png".format(out_dir, i))
            #transformed_image.popup()

            aligned_images.append(transformed_image)

        return aligned_images

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
        output = np.zeros(shape=images[0].raw().shape, dtype=images[0].raw().dtype)

        width, height = images[0].size()
        for y in range(0, height):
            for x in range(0, width):
                yxlaps = abs(laplacians[:, y, x])
                index = (np.where(yxlaps == max(yxlaps)))[0][0]
                output[y, x] = images[index].raw()[y, x]

        return Image(output)




