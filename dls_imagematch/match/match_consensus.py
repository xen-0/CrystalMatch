from __future__ import division

import math
import numpy as np

from .match_region import RegionMatcher
from dls_imagematch.util import Translate


class ConsensusMatcher:
    """ Matcher for finding the optimum point of overlap of two images. This works by using the iterative
    region matcher, but running it multiple times from slightly different starting positions, and then taking
    the most popular result to be the correct one.
    """
    def __init__(self, img_a, img_b):
        # The two images. The end result should map image B onto image A.
        self.img_a = img_a
        self.img_b = img_b

        # Starting guess for the translation
        self.initial = None
        self.grid_spacing = 0

        self.match_transform = None
        self.match_confidence = 0
        self.match_complete = False

    def match(self, initial, grid_spacing):
        """ Perform the matching operation and return the transform that best maps image B onto image A.
        """
        self.initial = initial
        self.grid_spacing = grid_spacing

        starting_points = self._make_starting_points(initial, grid_spacing)

        results = []

        for point in starting_points:
            matcher = RegionMatcher(self.img_a, self.img_b, point)
            matcher.skip_to_end()

            if matcher.match_complete:
                results.append(matcher.net_transform)

        # Determine which result is the most popular
        best_transform, confidence = self._best_translate(results)
        self.match_transform = best_transform
        self.match_confidence = confidence

        return self.match_transform

    @staticmethod
    def _make_starting_points(initial, increment):
        """ Make a grid of points around the initial guess to be used as starting points (translations) in
        the region matching procedures. Makes a 3x3 grid of points evenly spaced with the initial guess as
        the center.
        """
        # The grid spacing is a percentage of the size of the image
        cx, cy = initial.x, initial.y
        grid = [increment * i for i in range(-1, 2)]

        # Create the grid
        starting_points = []
        for del_x in grid:
            for del_y in grid:
                trans = Translate(cx + del_x, cy + del_y)
                starting_points.append(trans)

        return starting_points

    @staticmethod
    def _best_translate(results):
        """ Each run of the region matching procedure can have a different result. Group together results that
        are the same (or very similar), and return the result that has the largest group.
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

        # Find largest set
        set_lengths = map(len, groups)
        consensus = np.argmax(set_lengths)  # TODO: Check if tied for longest.

        print('Confidence:', str(len(groups[consensus]))+'/'+str(len(results)))
        confidence = len(groups[consensus]) / len(results)

        return groups[consensus][0], confidence

