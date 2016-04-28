from __future__ import division

import math

from .match_region import RegionMatcher
from dls_imagematch.util import Translate


class ConsensusMatcher:

    def __init__(self, img_a, img_b, initial):
        self.img_a = img_a
        self.img_b = img_b
        self.initial = initial

        self.match_complete = False
        self.net_transform = None

    def perform_match(self):

        starting_points = self._make_starting_points()

        results = []

        for point in starting_points:
            matcher = RegionMatcher(self.img_a, self.img_b, point)
            matcher.skip_to_end()

            if matcher.match_complete:
                print(str(point) + ",   " + str(matcher.net_transform))
                results.append(matcher.net_transform)

        best = self._best_translate(results)
        self.net_transform = best

    def _make_starting_points(self):
        starting_points = []

        inc = 0.05 * self.img_a.size[0]
        grid = [inc * i for i in range(-1, 2)]
        cx, cy = self.initial.x, self.initial.y

        for delx in grid:
            for dely in grid:
                trans = Translate(cx + delx, cy + dely)
                starting_points.append(trans)

        return starting_points

    def _best_translate(self, results):

        sets = [[results[0]]]

        for result in results:
            assigned = False
            for set in sets:
                prototype = set[0]
                delx = math.fabs(prototype.x - result.x)
                dely = math.fabs(prototype.y - result.y)
                if delx <= 2 and dely <= 2:
                    set.append(result)
                    assigned = True
                    break

            if not assigned:
                sets.append([result])

        best_set = []
        for set in sets:
            if len(set) > len(best_set):
                best_set = set

        return best_set[0]

