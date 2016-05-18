from __future__ import division

import cv2
import numpy as np
import math

from dls_imagematch.util import Translate, Image, Color, Point
from .transformation import Transformation


class FeatureMatchException(Exception):
    def __init__(self, message):
        super(FeatureMatchException, self).__init__(message)
        self.message = message


class _Match:
    def __init__(self, match, kp1, kp2):
        self._match = match
        self._kp1 = kp1
        self._kp2 = kp2

    def kp1(self): return self._kp1.pt

    def kp2(self): return self._kp2.pt


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

    def __init__(self, img_a, img_b):
        self.img_a = img_a
        self.img_b = img_b

        self.match_complete = False
        self.net_transform = None

    def match(self, method, adaptation):
        """ Perform the matching procedure. """
        '''
        try:
            self._perform_match()
        except AttributeError:
            msg = "Under Windows, this function only works correctly under OpenCV v2 (with Python 2.7) " \
                  "and not under OpenCV v3. This is a widely known and reported problem but it doesn't " \
                  "seem to have been fixed yet. Install Python 2.7 with OpenCV 2.4 and try again."
            raise OpenCvVersionError(msg)
        '''
        self.match_complete = False
        self.net_transform = None

        if method not in self.DETECTOR_TYPES:
            raise FeatureMatchException("No such feature matching method available: " + method)
        elif adaptation not in self.ADAPTATION_TYPE:
            raise FeatureMatchException("No such feature matching adaptation available: " + adaptation)

        self._perform_match(self.img_a, self.img_b, str(method), str(adaptation))

    def _perform_match(self, img1, img2, method, adaptation):

        if method == "Consensus":
            self.POPUP_RESULTS = False
            matches = self._find_matches_for_consensus(img1, img2, adaptation)
        else:
            matches = self._find_matches_for_method(img1, img2, method, adaptation)

        # Check that we have actually found some features
        min_matches = self.MINIMUM_MATCHES
        if len(matches) < min_matches:
            message = "Could not find the required minimum number of matches ({})!".format(min_matches)
            raise FeatureMatchException(message)

        # Calculate the Transform
        translation = self._calculate_median_translation(matches)
        homography = self._calculate_homography(matches)

        if homography is not None:
            transform = Transformation(homography)
        else:
            transform = Transformation.from_translation(translation)

        self.net_transform = transform
        self.match_complete = True
        self.POPUP_RESULTS = True

        '''
        warped = transform.inverse_transform_image(img_b, (img_a.width, img_a.height))

        img_a.popup()
        warped.popup()
        print(img_a.size, warped.size)
        blended = cv2.addWeighted(img_a.img, 0.5, warped.img, 0.5, 0)

        corners = img_b.bounds().corners()
        corners = transform.inverse_transform_points(corners)

        blended = Image(blended)
        blended.popup()
        blended.draw_polygon(corners)
        blended.popup()
        '''

    @staticmethod
    def _find_matches_for_consensus(img1, img2, adaptation):
        matches = []
        for method in FeatureMatcher.CONSENSUS_DETECTORS:
            try:
                method_matches = FeatureMatcher._find_matches_for_method(img1, img2, method, adaptation)
                matches.append(method_matches)
                print("{} - {} matches".format(method, len(matches)))
            except FeatureMatchException:
                print(method + " - 0 matches")

        return matches

    @staticmethod
    def _find_matches_for_method(img1, img2, method, adaptation):
        keypoints_1, des1 = FeatureMatcher._detect_features(img1, method, adaptation)
        keypoints_2, des2 = FeatureMatcher._detect_features(img2, method, adaptation)

        # Find matches
        raw_matches = FeatureMatcher._brute_force_descriptor_match(method, des1, des2, n_best=200)

        # Create wrapping _Match objects so the results are easier to pass around
        matches = []
        for match in raw_matches:
            kp1 = keypoints_1[match.queryIdx]
            kp2 = keypoints_2[match.trainIdx]
            matches.append(_Match(match, kp1, kp2))

        # Draw matches image
        if FeatureMatcher.POPUP_RESULTS:
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
        detector = cv2.FeatureDetector_create(adaptation + detector_method)
        extractor = cv2.DescriptorExtractor_create(extractor_method)

        # Get keypoints and descriptors
        keypoints = detector.detect(img.img, None)
        keypoints, descriptors = extractor.compute(img.img, keypoints)

        # Show the detected keypoints
        if FeatureMatcher.POPUP_RESULTS:
            FeatureMatcher._draw_keypoints(img, keypoints)

        return keypoints, descriptors

    @staticmethod
    def _brute_force_descriptor_match(method, descriptors_1, descriptors_2, n_best):
        """ For two sets of feature descriptors generated from 2 images, attempt to find all the matches,
        i.e. find features that occur in both images.
        """
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

    @staticmethod
    def _calculate_median_translation(matches):
        """ For a set of feature matches between two images, find the average (median) translation that maps
        one image to the other.
        """
        xs = []
        ys = []
        for match in matches:
            (x1, y1) = match.kp1()
            (x2, y2) = match.kp2()
            xs.append(x2-x1)
            ys.append(y2-y1)

        # Get median result
        x = -np.median(xs)
        y = -np.median(ys)

        return Translate(x, y)

    @staticmethod
    def _calculate_homography(matches):
        """ See:
        http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#findhomography

        The method RANSAC can handle practically any ratio of outliers but it needs a threshold to distinguish
        inliers from outliers. The method LMeDS does not need any threshold but it works correctly only when
        there are more than 50% of inliers. Finally, if there are no outliers and the noise is rather small,
        use the default method (method=0).
        """
        homography = None

        if len(matches) >= 4:
            src_pts = np.float32([m.kp1() for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([m.kp2() for m in matches]).reshape(-1, 1, 2)

            homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.LMEDS)
            pts = np.float32([[0, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, homography)

            print(homography)
            print(dst)

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
            point1 = match.kp1()
            point2 = match.kp2() + img2_pos
            # Draw a small circle at both co-ordinates
            out.draw_circle(center=point1, radius=4, color=Color.Blue(), thickness=1)
            out.draw_circle(center=point2, radius=4, color=Color.Blue(), thickness=1)

            # Draw a line between the two points
            out.draw_line(point1, point2, color=Color.Blue(), thickness=1)

        # Resize so that it fits on the screen
        factor = 1800 / out.width
        out = out.rescale(factor)
        out.popup("Matches")

    @staticmethod
    def _draw_keypoints(img, keypoints):
        marked_img = cv2.drawKeypoints(img.img, keypoints, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        Image(marked_img).popup("Keypoints")
