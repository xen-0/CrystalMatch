from .painter import FeaturePainter


class FeatureMatchResult:
    """ Encapsulates the results of an invocation of the feature matching process and provides some useful
    methods on those results. This object is returned to the client by FeatureMatcher.
    """
    def __init__(self, img1, img2, matches, transform):
        self.img1 = img1
        self.img2 = img2
        self.matches = matches
        self.transform = transform

        self.method = None
        self.method_adapt = None

    def matches_image(self, matches=None, highlight_matches=[]):
        if matches is None:
            matches = self._filtered_matches()
        painter = FeaturePainter(self.img1, self.img2)
        img = painter.draw_matches(matches, highlight_matches)
        return img

    def keypoints_image1(self):
        keypoints = [m.keypoint1() for m in self.matches]
        img = FeaturePainter.draw_keypoints(self.img1, keypoints)
        return img

    def keypoints_image2(self):
        keypoints = [m.keypoint2() for m in self.matches]
        img = FeaturePainter.draw_keypoints(self.img2, keypoints)
        return img

    def _filtered_matches(self):
        return [m for m in self.matches if m.is_in_transformation()]
