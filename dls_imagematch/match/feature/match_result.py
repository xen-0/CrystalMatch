from ._draw import FeaturePainter


class FeatureMatchResult:
    def __init__(self, img1, img2, matches, transform):
        self.img1 = img1
        self.img2 = img2
        self.matches = matches
        self.transform = transform

        self.method = None
        self.method_adapt = None

    def matches_image(self):
        img = FeaturePainter.draw_matches(self.img1, self.img2, self._filtered_matches())
        return img

    def keypoints_image1(self):
        keypoints = [m._kp1 for m in self.matches]
        img = FeaturePainter.draw_keypoints(self.img1, keypoints)
        return img

    def keypoints_image2(self):
        keypoints = [m._kp2 for m in self.matches]
        img = FeaturePainter.draw_keypoints(self.img2, keypoints)
        return img

    def _filtered_matches(self):
        return [m for m in self.matches if m.is_in_transformation()]
