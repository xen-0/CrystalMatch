from __future__ import division

from dls_imagematch.util import Point


class TrialTransforms:
    def __init__(self):
        self.transforms = [Point(0, 0)]

    def add_kings(self, distance):
        king_transforms = _king_trs(distance)
        self.transforms.extend(king_transforms)

    def compose_with(self, transformation):
        """ Compose all of the transformations with some other supplied transformation. """
        return [transformation + tr for tr in self.transforms]


def _floatify_args(fn):  # A decorator.
    def wrapper(*args):
        floatified_args = []
        for arg in args:
            try:
                arg = float(arg)
            except TypeError:
                pass
            floatified_args.append(arg)
        return fn(*floatified_args)
    return wrapper


@_floatify_args
def _king_trs(distance):
    # (Moves available to a King on a chess board.)
    # `distance` is the desired distance in actual pixels at the given wsf.
    dx = distance
    dy = distance

    return [
        # Horizontal/vertical moves.
        Point(+dx, 0),
        Point(-dx, 0),
        Point(0, +dy),
        Point(0, -dy),

        # Diagonal moves.
        Point(+dx, +dy),
        Point(-dx, +dy),
        Point(+dx, -dy),
        Point(-dx, -dy),
    ]