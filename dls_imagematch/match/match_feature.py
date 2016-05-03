from __future__ import division

import cv2
import numpy as np

from dls_imagematch.util import Translate, Image


class OpenCvVersionError(Exception):
    def __init__(self, message):
        super(OpenCvVersionError, self).__init__(message)
        self.message = message


class FeatureMatcher:
    """ Use feature matching to compare to images and align the second on the first.

    Note this only works correctly under OpenCV v2. Under v3, the function 'orb.detectAndCompute()'
    does not work properly for Python - it incorrectly raises an exception. This is a widely known
    and reported problem but it doesn't seem to have been fixed yet.
    """
    DETECTOR_TYPES = ["ORB", "SIFT", "SURF", "BRISK", "FAST", "STAR", "MSER", "GFTT", "HARRIS", "Dense", "SimpleBlob"]

    def __init__(self, img_a, img_b):
        self.img_a = img_a
        self.img_b = img_b

        self.match_complete = False
        self.net_transform = None

    def match(self, method):
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
        if method not in self.DETECTOR_TYPES:
            raise NotImplementedError("No such feature matching method available: " + method)

        self._perform_match(str(method))

    def _perform_match(self, method):
        img1 = self.img_a
        img2 = self.img_b

        kp1, des1 = self._detect_features(method, img1.img)
        kp2, des2 = self._detect_features(method, img2.img)

        # Find matches
        matches = self._find_matches(method, des1, des2)

        # Draw the best 55% of matches
        num = int(len(matches) * 0.55)
        self._draw_matches(img1.img, kp1, img2.img, kp2, matches[:num])

        # Calculate the Transform
        self.net_transform = self._calculate_transform(matches, kp1, kp2)
        self.match_complete = True

    @staticmethod
    def _detect_features(detector_method, img):
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
        detector = cv2.FeatureDetector_create(detector_method)
        extractor = cv2.DescriptorExtractor_create(extractor_method)

        # Get keypoints and descriptors
        keypoints = detector.detect(img, None)
        keypoints, descriptors = extractor.compute(img, keypoints)

        # Show the detected keypoints
        marked_img = cv2.drawKeypoints(img, keypoints, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        Image(marked_img).popup(detector_method + " Keypoints")

        return keypoints, descriptors

    @staticmethod
    def _find_matches(method, descriptors_1, descriptors_2):
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

        return matches

    @staticmethod
    def _calculate_transform(matches, keypoints_1, keypoints_2):
        """ For a set of feature matches between two images, find the average (median) translation that maps
        one image to the other.
        """
        xs = []
        ys = []
        for mat in matches:
            # Get the matching keypoints for each of the images
            img1_idx = mat.queryIdx
            img2_idx = mat.trainIdx

            # x - columns
            # y - rows
            (x1, y1) = keypoints_1[img1_idx].pt
            (x2, y2) = keypoints_2[img2_idx].pt

            xs.append(x2-x1)
            ys.append(y2-y1)

        # Draw matches.
        x = -np.median(xs)
        y = -np.median(ys)

        return Translate(x, y)

    @staticmethod
    def _draw_matches(img1, keypoints1, img2, keypoints2, matches):
        """ Based on original from from:
            http://stackoverflow.com/questions/20259025/module-object-has-no-attribute-drawmatches-opencv-python

        Implementation of a function that is available in OpenCV 3 but not in OpenCV 2.

        Makes an image that is a side-by-side of the two images, with detected features highlighted and lines
        drawn between matching features in the two images.
        """
        # Create a new output image that concatenates the two images together
        rows1 = img1.shape[0]
        cols1 = img1.shape[1]
        rows2 = img2.shape[0]
        cols2 = img2.shape[1]

        out = np.zeros((max([rows1, rows2]), cols1+cols2, 3), dtype='uint8')

        # Place the first image to the left
        out[:rows1, :cols1] = np.dstack([img1, img1, img1])

        # Place the next image to the right of it
        out[:rows2, cols1:] = np.dstack([img2, img2, img2])

        # For each pair of points we have between both images
        # draw circles, then connect a line between them
        for mat in matches:

            # Get the matching keypoints for each of the images
            img1_idx = mat.queryIdx
            img2_idx = mat.trainIdx

            # x - columns
            # y - rows
            (x1, y1) = keypoints1[img1_idx].pt
            (x2, y2) = keypoints2[img2_idx].pt

            # Draw a small circle at both co-ordinates
            radius = 4
            color = (255, 0, 0)  # blue
            thickness = 1
            cv2.circle(out, (int(x1), int(y1)), radius, color, thickness)
            cv2.circle(out, (int(x2)+cols1, int(y2)), radius, color, thickness)

            # Draw a line in between the two points
            # thickness = 1
            # colour blue
            cv2.line(out, (int(x1), int(y1)), (int(x2)+cols1, int(y2)), (255, 0, 0), 1)

        # Resize so that it fits on the screen
        img = Image(out)
        factor = 1800 / img.size[0]
        out = Image(out).rescale(factor)
        out.popup("Matches")

        # Also return the image if you'd like a copy
        return out
