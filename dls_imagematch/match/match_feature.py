from __future__ import division

import cv2
import numpy as np

from dls_imagematch.util import Translate, Image, Color, Point
from .transformation import Transformation


class FeatureMatchException(Exception):
    def __init__(self, message):
        super(FeatureMatchException, self).__init__(message)
        self.message = message


class _SingleFeatureMatch:
    """ Wrapper for the match and keypoint objects produced byt the OpenCV feature matching routines. Makes
    it easier to use and pass around this data. Only intended for internal use in the FeatureMatcher class.
    """
    def __init__(self, match, kp1, kp2):
        self._match = match
        self._kp1 = kp1
        self._kp2 = kp2

    def point1(self):
        return Point(self._kp1.pt[0], self._kp1.pt[1])

    def point2(self):
        return Point(self._kp2.pt[0], self._kp2.pt[1])


class FeatureMatcher:
    """ Use feature matching to compare to images and align the second on the first.

    Note this only works correctly under OpenCV v2. Under v3, the function 'orb.detectAndCompute()'
    does not work properly for Python - it incorrectly raises an exception. This is a widely known
    and reported problem but it doesn't seem to have been fixed yet.
    """
    DETECTOR_TYPES = ["ORB", "SIFT", "SURF", "BRISK", "FAST", "STAR", "MSER", "GFTT", "HARRIS", "Consensus", "Dense", "SimpleBlob"]
    ADAPTATION_TYPE = ["", "Grid", "Pyramid"]

    CONSENSUS_DETECTORS = ["ORB", "SIFT", "SURF", "BRISK", "FAST", "STAR", "MSER", "GFTT", "HARRIS"]

    POPUP_RESULTS = True
    MINIMUM_MATCHES = 1

    _OPENCV_VERSION_ERROR = "Under Windows, this function only works correctly under OpenCV v2 (with Python 2.7) " \
                            "and not under OpenCV v3. This is a widely known and reported problem but it doesn't " \
                            "seem to have been fixed yet. Install Python 2.7 with OpenCV 2.4 and try again."

    def __init__(self, img1, img2, img1_rect=None, img2_rect=None):
        """ Feature Matching between two images. If rectangular regions are provided, the routine will
        only consider features in those regions. """
        if img1_rect is None:
            img1_rect = img1.bounds()

        if img2_rect is None:
            img2_rect = img2.bounds()

        self.img1 = img1.crop(img1_rect)
        self.img2 = img2.crop(img2_rect)

        self.img1_offset = img1_rect.top_left()
        self.img2_offset = img2_rect.top_left()

        self.match_complete = False
        self.net_transform = None

    def match(self, method, adaptation, translation_only=False):
        """ Perform a feature matching operation between the two selected images (or image regions if
        specified. The resulting transformation can be applied to a point in Image/Region 1 coordinates
        to map it to its matching point in Image 2 coordinates.

        Parameters
        ----------
        method - Name (string) of the OpenCV feature matching method to use (one of DETECTOR_TYPES)
        adaptation - Feature matching adaptation (one of ADAPTATION_TYPE)
        translation_only - If True, consider only the translation component of the match transformation.
        """
        self.match_complete = False
        self.net_transform = None

        if method not in self.DETECTOR_TYPES:
            raise FeatureMatchException("No such feature matching method available: " + method)
        elif adaptation not in self.ADAPTATION_TYPE:
            raise FeatureMatchException("No such feature matching adaptation available: " + adaptation)

        transform = self._perform_match(self.img1, self.img2, str(method), str(adaptation), translation_only)
        return transform

    def _perform_match(self, img1, img2, method, adaptation, translation_only):
        """ Call the correct feature matching function (normal or consensus). And determine the
        proper transformation from the match results. """
        if method == "Consensus":
            FeatureMatcher.POPUP_RESULTS = False
            matches = self._find_matches_for_consensus(img1, img2, adaptation)
        else:
            matches = self._find_matches_for_method(img1, img2, method, adaptation)

        # Check that we have actually found some features
        min_matches = self.MINIMUM_MATCHES
        if len(matches) < min_matches:
            message = "Could not find the required minimum number of matches ({})!".format(min_matches)
            raise FeatureMatchException(message)

        # Calculate the average translation from the match deltas
        translation = self._calculate_median_translation(matches)

        # Calculate the full transformation the maps image 1 to image 2 (includes rotation, scaling, skew)
        homography = None
        if not translation_only:
            homography = self._calculate_homography(matches)

        transform = Transformation(translation, homography)

        self.net_transform = transform
        self.match_complete = True
        self.POPUP_RESULTS = True

        return transform

    @staticmethod
    def _find_matches_for_consensus(img1, img2, adaptation):
        """ Perform feature matching for each method in the consensus list, and aggregate the match results."""
        matches = []
        for method in FeatureMatcher.CONSENSUS_DETECTORS:
            try:
                method_matches = FeatureMatcher._find_matches_for_method(img1, img2, method, adaptation)
                matches.extend(method_matches)
                # print("{} - {} matches".format(method, len(method_matches)))
            except FeatureMatchException:
                print(method + " - fail")

        return matches

    @staticmethod
    def _find_matches_for_method(img1, img2, method, adaptation):
        """ Perform feature matching using the specified method and return a list of matches. """
        # Detect features in both the images
        keypoints_1, des1 = FeatureMatcher._detect_features(img1, method, adaptation)
        keypoints_2, des2 = FeatureMatcher._detect_features(img2, method, adaptation)

        # Find matches between feature sets
        raw_matches = FeatureMatcher._brute_force_descriptor_match(method, des1, des2, n_best=200)

        # Create wrapping _SingleFeatureMatch objects so the results are easier to pass around
        matches = []
        for match in raw_matches:
            kp1 = keypoints_1[match.queryIdx]
            kp2 = keypoints_2[match.trainIdx]
            matches.append(_SingleFeatureMatch(match, kp1, kp2))

        # Draw matches image
        if FeatureMatcher.POPUP_RESULTS and len(matches) > 0:
            FeatureMatcher._draw_matches(img1, img2, matches)

        return matches

    @staticmethod
    def _detect_features(img, detector_method, adaptation):
        """ Detect interesting features in the image and generate descriptors. A keypoint identifies the
        location and orientation of a feature, and a descriptor is a vector of numbers that describe the
        various attributes of the feature. By generating descriptors, we can compare the set of features
        on two images and find matches between them.
        """
        # Sift, Surf, and Orb have their own descriptor extraction methods.
        if detector_method in ["SIFT", "SURF", "ORB"]:
            extractor_method = detector_method
        else:
            extractor_method = "BRIEF"

        # Create the feature detector and descriptor extractor
        try:
            detector = cv2.FeatureDetector_create(adaptation + detector_method)
            extractor = cv2.DescriptorExtractor_create(extractor_method)
        except AttributeError:
            raise FeatureMatchException(FeatureMatcher._OPENCV_VERSION_ERROR)

        # Get keypoints and descriptors
        keypoints = detector.detect(img.img, None)
        keypoints, descriptors = extractor.compute(img.img, keypoints)

        if descriptors is None:
            keypoints, descriptors = [], []

        # Show the detected keypoints
        if FeatureMatcher.POPUP_RESULTS and len(keypoints) > 0:
            FeatureMatcher._draw_keypoints(img, keypoints)

        return keypoints, descriptors

    @staticmethod
    def _brute_force_descriptor_match(method, descriptors_1, descriptors_2, n_best):
        """ For two sets of feature descriptors generated from 2 images, attempt to find all the matches,
        i.e. find features that occur in both images.
        """
        if len(descriptors_1) == 0 or len(descriptors_2) == 0:
            return []

        # TODO: Try out a FLANN based matcher
        # Create Brute-Force matcher object
        if method in ["SIFT", "SURF"]:
            matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        else:
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Match descriptors.
        matches = matcher.match(descriptors_1, descriptors_2)

        # Sort them in the order of their distance.
        matches = sorted(matches, key=lambda x: x.distance)

        return matches[:n_best]

    def _calculate_median_translation(self, matches):
        """ For a set of feature matches between two images, find the average (median) translation that maps
        one image to the other.
        """
        deltas = []
        for match in matches:
            point1 = match.point1() + self.img1_offset
            point2 = match.point2() + self.img2_offset
            delta = point2 - point1
            deltas.append(delta)

        # Get median result
        x = -np.median([d.x for d in deltas])
        y = -np.median([d.y for d in deltas])

        return Translate(x, y)

    def _calculate_homography(self, matches):
        """ See:
        http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#findhomography

        The method RANSAC can handle practically any ratio of outliers but it needs a threshold to distinguish
        inliers from outliers. The method LMeDS does not need any threshold but it works correctly only when
        there are more than 50% of inliers. Finally, if there are no outliers and the noise is rather small,
        use the default method (method=0).
        """
        homography = None

        if len(matches) >= 4:
            img1_pts = [m.point1() + self.img1_offset for m in matches]
            img1_pts = np.float32([p.tuple() for p in img1_pts]).reshape(-1, 1, 2)
            img2_pts = [m.point2() + self.img2_offset for m in matches]
            img2_pts = np.float32([p.tuple() for p in img2_pts]).reshape(-1, 1, 2)

            homography, mask = cv2.findHomography(img1_pts, img2_pts, cv2.LMEDS)
            pts = np.float32([[0, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, homography)

        return homography

    @staticmethod
    def _draw_matches(img1, img2, matches):
        """ Implementation of a function that is available in OpenCV 3 but not in OpenCV 2.
        Makes an image that is a side-by-side of the two images, with detected features highlighted and lines
        drawn between matching features in the two images.
        """
        # Create a new output image that concatenates the two images together
        w1, h1 = img1.size
        w2, h2 = img2.size
        img1_pos, img2_pos = Point(0, 0), Point(w1, 0)
        out = Image.blank(w1+w2, max(h1, h2))
        out.paste(img1, img1_pos)
        out.paste(img2, img2_pos)

        # For each pair of points we have between both images draw circles, then connect a line between them
        for match in matches:
            point1 = match.point1()
            point2 = match.point2() + img2_pos
            # Draw a small circle at both co-ordinates
            out.draw_circle(point=point1, radius=4, color=Color.Blue(), thickness=1)
            out.draw_circle(point=point2, radius=4, color=Color.Blue(), thickness=1)

            # Draw a line between the two points
            out.draw_line(point1, point2, color=Color.Blue(), thickness=1)

        # Resize so that it fits on the screen
        factor = 1000 / out.width
        out = out.rescale(factor)
        out.popup("Matches")

    @staticmethod
    def _draw_keypoints(img, keypoints):
        """ Draw the list of keypoints to the specified image and display it as a popup window. """
        marked_img = cv2.drawKeypoints(img.img, keypoints, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        Image(marked_img).popup("Keypoints")
