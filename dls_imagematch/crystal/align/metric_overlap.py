from __future__ import division

import cv2
import numpy as np

from .overlay import Overlayer


class OverlapMetric:

    def __init__(self, img1, img2, trial_transforms):
        self.img1 = img1
        self.img2 = img2
        self.trial_transforms = trial_transforms

    def best_transform(self, starting_transform):
        """ For a TrialTransforms object, return the transform which has the
        minimum metric value.
        """
        metrics = []

        transforms = [starting_transform + tr for tr in self.trial_transforms]

        for transform in transforms:
            offset = transform.intify()
            metric = self.calculate_overlap_metric(offset)
            metrics.append(metric)

        # Extract the best transformation (and associated abs_diff image)
        best = np.argmin(metrics)
        best_transform = transforms[best]

        # Whether or not the best transform candidate is actually the identity (i.e. no change)
        is_identity = (best == 0)

        return best_transform, is_identity

    def calculate_overlap_metric(self, offset):
        """ For two images, A and B, where B is offset relative to A, calculate the average
        per pixel absolute difference of the region of overlap of the two images.

        Return the value of this metric as well as an image showing the per pixel absolute
        differences. In the returned image, darker areas indicate greater differences in the
        overlap whereas lighter areas indicate more similarity.
        """
        cr1, cr2 = Overlayer.get_overlap_regions(self.img1, self.img2, offset)

        absdiff_img = cv2.absdiff(cr1.img(), cr2.img())
        metric = np.sum(absdiff_img) / absdiff_img.size

        return metric
