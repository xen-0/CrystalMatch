import numpy as np
import cv2

from dls_imagematch.util import Image
from dls_imagematch.match import FeatureMatcher


class FocusStack:
    def __init__(self, images, config):
        self._images = images
        self._config = config

    def composite(self, with_align=True):
        """ Finds the points of best focus in all images and produces a merged result """
        cfg = self._config

        if with_align:
            method = cfg.align_method.value()
            adapt = cfg.align_adapt.value()
            out_dir = cfg.output_dir.value()
            images = self._align_images(self._images, method, adapt, out_dir)
        else:
            images = self._images

        kernel_size = cfg.kernel_size.value()
        blur_radius = cfg.blur_radius.value()
        laplacians = self._compute_laplacians(images, kernel_size, blur_radius)

        focused_image = self._determine_focused_pixels(images, laplacians)

        return focused_image

    @staticmethod
    def _align_images(images, method, adapt, out_dir):
        aligned_images = []

        # TODO - Frame-by-frame alignment where each frame is aligned with the previous one. This will mean
        # TODO - that the transform for a frame needs to be the product of all transforms that proceeded it

        img1 = images[0]
        for i in range(1, len(images)):
            print("Aligning image {}/{}".format(i+1, len(images)))
            #img1 = images[i-1]
            img2 = images[i]
            FeatureMatcher.POPUP_RESULTS = False
            matcher = FeatureMatcher(img1, img2)

            transform = matcher.match(method, adapt)
            transformed_img = transform.inverse_transform_image(img2, img2.size)
            transformed_img.save("{}aligned{}.png".format(out_dir, i))
            #transformed_img.popup()

            aligned_images.append(transformed_img)

        return aligned_images

    @staticmethod
    def _compute_laplacians(images, kernel_size, blur_size):
        """ Compute the gradient map of the image """

        print("Computing the laplacian of the blurred images")
        laps = []
        for i in range(len(images)):
            print "Lap {}".format(i)
            img = images[i].to_mono().img
            blurred = cv2.GaussianBlur(img, (blur_size, blur_size), 0)
            result = cv2.Laplacian(blurred, cv2.CV_64F, ksize=kernel_size)
            laps.append(result)

        laps = np.asarray(laps)
        print "Shape of array of laplacians = {}".format(laps.shape)

        return laps

    @staticmethod
    def _determine_focused_pixels(images, laplacians):
        output = np.zeros(shape=images[0].img.shape, dtype=images[0].img.dtype)

        width, height = images[0].width, images[0].height
        for y in range(0, height):
            for x in range(0, width):
                yxlaps = abs(laplacians[:, y, x])
                index = (np.where(yxlaps == max(yxlaps)))[0][0]
                output[y, x] = images[index].img[y, x]

        return Image(output)




