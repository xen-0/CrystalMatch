"""

Simple Focus Stacker

    Author:     Charles McGuinness (charles@mcguinness.us)
    Copyright:  Copyright 2015 Charles McGuinness
    License:    Apache License 2.0


This code will take a series of images and merge them so that each
pixel is taken from the image with the sharpest focus at that location.

The logic is roughly the following:

1.  Align the images.  Changing the focus on a lens, even
    if the camera remains fixed, causes a mild zooming on the images.
    We need to correct the images so they line up perfectly on top
    of each other.

2.  Perform a gaussian blur on all images

3.  Compute the laplacian on the blurred image to generate a gradient map

4.  Create a blank output image with the same size as the original input
    images

4.  For each pixel [x,y] in the output image, copy the pixel [x,y] from
    the input image which has the largest gradient [x,y]
    

This algorithm was inspired by the high-level description given at

http://stackoverflow.com/questions/15911783/what-are-some-common-focus-stacking-algorithms

"""

import numpy as np
import cv2

from dls_imagematch.util import Image
from dls_imagematch.match import FeatureMatcher


class FocusStack:
    def __init__(self, images):
        self._images = images

    def composite(self, with_align=True):
        """ Finds the points of best focus in all images and produces a merged result """
        if with_align:
            images = self._align_images(self._images)
        else:
            images = self._images

        laplacians = self._compute_laplacians(images)

        focused_image = self._determine_focused_pixels(images, laplacians)

        return focused_image

    @staticmethod
    def _align_images(images):
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


            transform = matcher.match("SURF", "")
            transformed_img = transform.inverse_transform_image(img2, img2.size)
            transformed_img.save("../test-output/focus/aligned{}.png".format(i))
            #transformed_img.popup()

            aligned_images.append(transformed_img)

        return aligned_images

    @staticmethod
    def _compute_laplacians(images):
        """ Compute the gradient map of the image """
        # YOU SHOULD TUNE THESE VALUES TO SUIT YOUR NEEDS
        kernel_size = 5         # Size of the laplacian window
        blur_size = 5           # How big of a kernal to use for the gaussian blur
                                # Generally, keeping these two values the same or very close works well
                                # Also, odd numbers, please...

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

        height, width = images[0].img.shape
        for y in range(0, height):
            for x in range(0, width):
                yxlaps = abs(laplacians[:, y, x])
                index = (np.where(yxlaps == max(yxlaps)))[0][0]
                output[y, x] = images[index].img[y, x]

        return Image(output)




