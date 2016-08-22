from __future__ import division

from .matcher import FeatureMatcher
from .match import SingleFeatureMatch


class BoundedFeatureMatcher(FeatureMatcher):
    """ Specialization of feature matcher which allows user to specify sub regions of the two images.
    When performing the matching operations, only features in these regions will be considered. """
    def __init__(self, img1, img2, detector_config, img1_rect, img2_rect):
        FeatureMatcher.__init__(self, img1, img2, detector_config)

        if img1_rect is None:
            img1_rect = img1.bounds()

        if img2_rect is None:
            img2_rect = img2.bounds()

        self.img1 = img1.crop(img1_rect)
        self.img2 = img2.crop(img2_rect)

        self.img1_offset = img1_rect.top_left()
        self.img2_offset = img2_rect.top_left()

    def _matches_from_raw(self, raw_matches, keypoints1, keypoints2, method):
        matches = SingleFeatureMatch.from_cv2_matches(raw_matches, keypoints1, keypoints2, method)
        for match in matches:
            match.set_offsets(self.img1_offset, self.img2_offset)

        return matches
