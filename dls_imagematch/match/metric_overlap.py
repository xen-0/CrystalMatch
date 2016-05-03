from __future__ import division

import cv2
import numpy as np

from dls_imagematch.match.overlay import Overlayer
from dls_imagematch.util.image import Image


class OverlapMetric:

    def __init__(self, img_a, img_b, trial_transforms):
        self.img_a = img_a
        self.img_b = img_b
        self.trial_transforms = trial_transforms

    def best_transform(self, starting_transform):
        """ For a TrialTransforms object, return the transform which has the
        minimum metric value.
        """
        metrics = []

        transforms = self.trial_transforms.compose_with(starting_transform)

        for transform in transforms:
            offset = (int(transform.x), int(transform.y))
            metric = self.calculate_overlap_metric(offset)
            metrics.append(metric)

        # Extract the best transformation (and associated abs_diff image)
        best = np.argmin(metrics)
        best_transform = transforms[best]

        # Whether or not the best transform candidate is actually the identity (i.e. no change)
        is_identity = (best == 0)

        return best_transform, is_identity

    def create_overlay_image(self, overlay_img, transform):
        # Make a copy of A, the background image
        background = self.img_a.copy()

        # Determine size of B, which is the size of the overlay image area.
        working_size = self.img_b.size
        w, h = working_size

        # Determine offset amount
        x, y = transform.x, transform.y

        # Define the rectangle that will be pasted to in the background image
        roi = (x, y, x+w, y+h)

        # Paste the overlay image to the background and draw a rectangle around it
        overlay = Image(overlay_img, self.img_b.pixel_size)
        background.paste(overlay, xOff=max(x, 0), yOff=max(y, 0))
        background.draw_rectangle(roi)

        return background

    def calculate_overlap_metric(self, offset):
        """ For two images, A and B, where B is offset relative to A, calculate the average
        per pixel absolute difference of the region of overlap of the two images.

        Return the value of this metric as well as an image showing the per pixel absolute
        differences. In the returned image, darker areas indicate greater differences in the
        overlap whereas lighter areas indicate more similarity.
        """
        cr1, cr2 = Overlayer.get_overlap_regions(self.img_a, self.img_b, offset)

        absdiff_img = cv2.absdiff(cr1, cr2)
        metric = np.sum(absdiff_img) / absdiff_img.size

        return metric
