from dls_imagematch.util import Point


class SingleFeatureMatch:
    """ Wrapper for the match and keypoint objects produced by the OpenCV feature matching routines. Makes
    it easier to use and pass around this data.
    """
    def __init__(self, match, feature1, feature2, method):
        self._match = match
        self._feature1 = feature1
        self._feature2 = feature2
        self._method = method
        self._offset1 = Point(0, 0)
        self._offset2 = Point(0, 0)
        self._point2_projected = None
        self._included_in_transformation = True

    def method(self):
        return self._method

    def reprojection_error(self):
        if self._point2_projected is not None:
            return self.point2().distance_to(self._point2_projected)
        else:
            return 1e6

    def is_in_transformation(self):
        return self._included_in_transformation

    def distance(self):
        return self._match.distance

    def point1(self):
        return self.img_point1() + self._offset1

    def point2(self):
        return self.img_point2() + self._offset2

    def point2_projected(self):
        return self._point2_projected

    def img_point1(self):
        return self._feature1.point()

    def img_point2(self):
        return self._feature2.point()

    def set_offsets(self, offset1, offset2):
        self._offset1 = offset1
        self._offset2 = offset2

    def set_point2_projected(self, point):
        self._point2_projected = point

    def set_in_transformation(self, in_transformation):
        self._included_in_transformation = in_transformation

    @staticmethod
    def from_cv2_matches(cv2_matches, features1, features2, detector):
        func = SingleFeatureMatch.from_cv2_match
        return [func(match, features1, features2, detector) for match in cv2_matches]

    @staticmethod
    def from_cv2_match(cv2_match, features1, features2, detector):
        f1 = features1[cv2_match.queryIdx]
        f2 = features2[cv2_match.trainIdx]
        method = detector.adaptation() + detector.detector()
        cv2_match = SingleFeatureMatch(cv2_match, f1, f2, method)
        return cv2_match

