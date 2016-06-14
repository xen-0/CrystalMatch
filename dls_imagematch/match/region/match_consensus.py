from __future__ import division

import math
import multiprocessing
from functools import partial
from multiprocessing import Pool

import numpy as np

from .match_region import RegionMatcher
from dls_imagematch.util import Point


class RegionConsensusMatcher:
    """ Matcher for finding the optimum point of overlap of two images. This works by using the iterative
    region matcher, but running it multiple times from slightly different starting positions, and then taking
    the most popular result to be the correct one.
    """
    PARALLEL = False

    def __init__(self, img1, img2):
        # The two images. The end result should map image B onto image A.
        self.img1 = img1
        self.img2 = img2

        # Starting guess for the translation
        self.initial = None
        self.grid_spacing = 0
        self.grid_size = 3

        self.match_transform = None
        self.match_confidence = 0
        self.match_complete = False

    def match(self, initial, grid_size, grid_space):
        """ Perform the matching operation and return the transform that best maps image B onto image A.
        """
        self.initial = initial
        self.grid_spacing = grid_space
        self.grid_size = int(grid_size)

        # Create a set of starting points to use in the region matching
        starting_points = self._make_starting_points(initial, grid_size, grid_space)
        results = self._get_match_results(starting_points)

        # Determine which result is the most popular
        best_translate, confidence = self._determine_best_result(results)
        self.match_transform = best_translate
        self.match_confidence = confidence
        return self.match_transform

    def _get_match_results(self, starting_points):
        if RegionConsensusMatcher.PARALLEL:
            results = self._match_parallel(starting_points)
        else:
            results = self._match_single(starting_points)

        results = [r for r in results if r is not None]
        return results

    def _match_single(self, starting_points):
        results = []
        for point in starting_points:
            result = _perform_region_match(self.img1, self.img2, point)
            results.append(result)
        return results

    def _match_parallel(self, starting_points):
        # Parallel algorithm is about the same speed with 9 points, but gets faster with more points
        cpu_count = multiprocessing.cpu_count() - 1
        worker_pool = Pool(processes=cpu_count)
        partial_matcher = partial(_perform_region_match, self.img1, self.img2)
        results = worker_pool.map(partial_matcher, starting_points)
        return results

    @staticmethod
    def _make_starting_points(initial, grid_size, increment):
        """ Make a grid of points around the initial guess to be used as starting points (translations) in
        the region matching procedures. Makes a 3x3 grid of points evenly spaced with the initial guess as
        the center.
        """
        # The grid spacing is a percentage of the size of the image
        cx, cy = initial.x, initial.y
        grid = [increment * i for i in range(-grid_size, grid_size+1)]

        starting_points = []
        for del_x in grid:
            for del_y in grid:
                point = Point(cx + del_x, cy + del_y)
                starting_points.append(point)

        return starting_points

    def _determine_best_result(self, results):
        """ Each run of the region matching procedure can have a different result. Group together results that
        are the same (or very similar), and return the result that has the largest group.
        """
        groups = self._group_similar_results(results)

        # Find largest set
        set_lengths = map(len, groups)
        consensus = np.argmax(set_lengths)  # TODO: Check if tied for longest.

        print('Confidence:', str(len(groups[consensus]))+'/'+str(len(results)))
        confidence = len(groups[consensus]) / len(results)

        return groups[consensus][0], confidence

    def _group_similar_results(self, results):
        groups = []
        for result in results:
            group = self._find_matching_group(result, groups)
            group.append(result)

            if group not in groups:
                groups.append(group)

        return groups

    def _find_matching_group(self, result, groups):
        for group in groups:
            if self._is_within_2_px(group[0], result):
                return group
        return []

    @staticmethod
    def _is_within_2_px(prototype, result):
        del_x = math.fabs(prototype.x - result.x)
        del_y = math.fabs(prototype.y - result.y)
        return del_x <= 2 and del_y <= 2


def _perform_region_match(img1, img2, point):
    matcher = RegionMatcher(img1, img2, point)
    matcher.skip_to_end()

    result = None
    if matcher.match_complete:
        result = matcher.net_transform

    return result
