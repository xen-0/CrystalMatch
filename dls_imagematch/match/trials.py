from dls_imagematch.util.translate import Translate


class TrialTransforms:
    def __init__(self):
        self.transforms = [Translate(0,0)]

    def add_kings(self, distance):
        king_transforms = _king_trs(distance)
        self.transforms.extend(king_transforms)

    def compose_with(self, transformation):
        """ Compose all of the transformations with some other supplied transformation
        """
        return [transformation.offset(tr) for tr in self.transforms]


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
        Translate(+dx, 0),
        Translate(-dx, 0),
        Translate(0, +dy),
        Translate(0, -dy),

        # Diagonal moves.
        Translate(+dx, +dy),
        Translate(-dx, +dy),
        Translate(+dx, -dy),
        Translate(-dx, -dy),
    ]