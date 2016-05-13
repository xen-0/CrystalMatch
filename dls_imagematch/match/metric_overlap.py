from __future__ import division

import cv2
import numpy as np

from dls_imagematch.match.overlay import Overlayer


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
            offset = transform.to_point().intify()
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
        cr1, cr2 = Overlayer.get_overlap_regions(self.img_a, self.img_b, offset)

        absdiff_img = cv2.absdiff(cr1.img, cr2.img)
        metric = np.sum(absdiff_img) / absdiff_img.size

        return metric
