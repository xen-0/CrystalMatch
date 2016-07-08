from dls_imagematch.util import Point


class SingleFeatureMatch:
    """ Wrapper for the match and keypoint objects produced by the OpenCV feature matching routines. Makes
    it easier to use and pass around this data.
    """
    def __init__(self, match, kp1, kp2, method):
        self._match = match
        self._kp1 = kp1
        self._kp2 = kp2
        self._method = method
        self._offset1 = Point(0, 0)
        self._offset2 = Point(0, 0)
        self._included_in_transformation = True

    def method(self):
        return self._method

    def is_in_transformation(self):
        return self._included_in_transformation

    def distance(self):
        return self._match.distance

    def keypoint1(self):
        return self._kp1

    def keypoint2(self):
        return self._kp2

    def point1(self):
        return self.img_point1() + self._offset1

    def point2(self):
        return self.img_point2() + self._offset2

    def img_point1(self):
        return Point(self._kp1.pt[0], self._kp1.pt[1])

    def img_point2(self):
        return Point(self._kp2.pt[0], self._kp2.pt[1])

    def set_offsets(self, offset1, offset2):
        self._offset1 = offset1
        self._offset2 = offset2

    def set_in_transformation(self, in_transformation):
        self._included_in_transformation = in_transformation

    @staticmethod
    def from_cv2_matches(cv2_matches, keypoints1, keypoints2, detector):
        func = SingleFeatureMatch.from_cv2_match
        return [func(match, keypoints1, keypoints2, detector) for match in cv2_matches]

    @staticmethod
    def from_cv2_match(cv2_match, keypoints1, keypoints2, detector):
        kp1 = keypoints1[cv2_match.queryIdx]
        kp2 = keypoints2[cv2_match.trainIdx]
        method = detector.adaptation + detector.detector
        cv2_match = SingleFeatureMatch(cv2_match, kp1, kp2, method)
        return cv2_match

