from dls_imagematch.util import Point


class SingleFeatureMatch:
    """ Wrapper for the match and keypoint objects produced byt the OpenCV feature matching routines. Makes
    it easier to use and pass around this data. Only intended for internal use in the FeatureMatcher class.
    """
    def __init__(self, match, kp1, kp2):
        self._match = match
        self._kp1 = kp1
        self._kp2 = kp2
        self._offset1 = Point(0, 0)
        self._offset2 = Point(0, 0)

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

    @staticmethod
    def matches_from_raw(raw_matches, keypoints1, keypoints2):
        matches = []
        for match in raw_matches:
            kp1 = keypoints1[match.queryIdx]
            kp2 = keypoints2[match.trainIdx]
            matches.append(SingleFeatureMatch(match, kp1, kp2))
        return matches
