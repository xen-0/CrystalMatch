from __future__ import division

import cv2
import numpy as np
import math

from dls_imagematch.util import Translate, Image


class FeatureMatchException(Exception):
    def __init__(self, message):
        super(FeatureMatchException, self).__init__(message)
        self.message = message


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
    MINIMUM_FEATURES = 1

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

        if method == "Consensus":
            self._perform_consensus_match()
        else:
            result = self._perform_match(str(method), str(adaptation), self.img_a, self.img_b)
            if result is not None:
                self.net_transform = result
                self.match_complete = True

    def _perform_consensus_match(self):
        FeatureMatcher.POPUP_RESULTS = False

        results = []
        for method in FeatureMatcher.CONSENSUS_DETECTORS:
            print(method)
            try:
                result = self._perform_match(method, "", self.img_a, self.img_b)
                results.append(result)
                print(result)
            except FeatureMatchException:
                pass

        # Raise exception if no results were found
        if len(results) == 0:
            raise FeatureMatchException("No feature matching technique returned a successful match.")

        best_result, confidence = self._best_consensus_result(results)
        print("Best: " + str(best_result))

        self.net_transform = best_result
        self.match_complete = True

        FeatureMatcher.POPUP_RESULTS = True
        return self.net_transform

    @staticmethod
    def _perform_match(method, adaptation, img_a, img_b):

        kp1, des1 = FeatureMatcher._detect_features(img_a.img, method, adaptation)
        kp2, des2 = FeatureMatcher._detect_features(img_b.img, method, adaptation)

        # Check that we have actually found some features
        if len(kp1) < FeatureMatcher.MINIMUM_FEATURES or len(kp2) < FeatureMatcher.MINIMUM_FEATURES:
            message = "Could not find the required minimum number of features (" \
                      + str(FeatureMatcher.MINIMUM_FEATURES) + ") in at least 1 image!"
            raise FeatureMatchException(message)

        # Find matches
        matches = FeatureMatcher._find_matches(method, des1, des2, n_best=200)

        # Draw matches image
        if FeatureMatcher.POPUP_RESULTS:
            FeatureMatcher._draw_matches(img_a.img, kp1, img_b.img, kp2, matches)

        # Calculate the Transform
        result = FeatureMatcher._calculate_median_translation(matches, kp1, kp2)

        # DEBUG FUN
        from .transformation import Transformation
        homography = FeatureMatcher._calculate_homography(matches, kp1, kp2)
        if homography is not None:
            trans = Transformation(homography)
        else:
            trans = Transformation.from_translation(result)

        warped = trans.inverse_transform_image(img_b, (img_a.width, img_a.height))

        img_a.popup()
        warped.popup()
        print(img_a.size, warped.size)
        blended = cv2.addWeighted(img_a.img, 0.5, warped.img, 0.5, 0)

        corners = img_b.bounds().corners()
        corners = trans.inverse_transform_points(corners)

        blended = Image(blended)
        blended.popup()
        blended.draw_polygon(corners)
        blended.popup()


        return result

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
        keypoints = detector.detect(img, None)
        keypoints, descriptors = extractor.compute(img, keypoints)

        # Show the detected keypoints
        if FeatureMatcher.POPUP_RESULTS:
            marked_img = cv2.drawKeypoints(img, keypoints, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            Image(marked_img).popup(detector_method + " Keypoints")

        return keypoints, descriptors

    @staticmethod
    def _find_matches(method, descriptors_1, descriptors_2, n_best):
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
    def _calculate_median_translation(matches, keypoints_1, keypoints_2):
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

        # Get median result
        x = -np.median(xs)
        y = -np.median(ys)
        print(x, y)
        return Translate(x, y)

    @staticmethod
    def _calculate_homography(matches, keypoints_1, keypoints_2):
        homography = None
        # TEST - calculate transform
        if len(matches) >= 4:
            src_pts = np.float32([keypoints_1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([keypoints_2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

            # see: http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#findhomography
            # The method RANSAC can handle practically any ratio of outliers but it needs a threshold to distinguish
            # inliers from outliers. The method LMeDS does not need any threshold but it works correctly only when
            # there are more than 50% of inliers. Finally, if there are no outliers and the noise is rather small,
            # use the default method (method=0).
            homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.LMEDS)
            pts = np.float32([[0, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, homography)

            print(homography)
            print(dst)

        return homography


    @staticmethod
    def _best_consensus_result(results):
        """ Each method used in the consensus match will have a different result. Group
        together results that are the same (or very similar), and return the result that
        has the largest group.
        """
        groups = []

        # Divide the results into sub-groups of the same/similar results
        for result in results:
            assigned = False
            for group in groups:
                prototype = group[0]
                # If the result is within 2 pixels of the group, add it to the group
                del_x = math.fabs(prototype.x - result.x)
                del_y = math.fabs(prototype.y - result.y)
                if del_x <= 2 and del_y <= 2:
                    group.append(result)
                    assigned = True
                    break

            # Assign to new group
            if not assigned:
                groups.append([result])

        # TODO - resolve ties by which result had the best agreement values (distances) for its set of matches
        # Find largest set
        set_lengths = map(len, groups)
        consensus = np.argmax(set_lengths)  # TODO: Check if tied for longest.
        best_set = groups[consensus]

        # Find average
        x_mean = sum([result.x for result in best_set]) / len(best_set)
        y_mean = sum([result.y for result in best_set]) / len(best_set)
        best_result = Translate(x_mean, y_mean)

        # Confidence of consensus
        print('Confidence:', str(len(best_set))+'/'+str(len(results)))
        confidence = len(best_set) / len(results)

        return best_result, confidence

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
