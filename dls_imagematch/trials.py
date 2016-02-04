import dls_imagematch.transforms as tlib  # Contains `Transform` class.


class TrialTransforms:
    def __init__(self, original_size):
        self.transforms = [tlib.Transform.identity()]
        self.orginal_size = original_size

    def add_kings(self, distance, scale):
        king_transforms = _king_trs(distance, scale, self.orginal_size)
        self.transforms.extend(king_transforms)

    def list(self):
        """ Return a list of the transformations, randomizing any random ones
        """
        return [tr() if isinstance(tr, tlib.RandomTransformer)
                         else tr for tr in self.transforms]

    def compose_with(self, transformation):
        """ Compose all of the transformations with some other supplied transformation
        """
        return [tr * transformation for tr in self.list()]


    def compose_matrices(self, new_size, transformation):
        matrices = [tr(new_size) for tr in self.compose_with(transformation)]
        return matrices


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
def _king_trs(distance, wsf, orig_working_size):
    # (Moves available to a King on a chess board.)
    # `distance` is the desired distance in actual pixels at the given wsf.
    d, f, (o_w, o_h) = distance, wsf, orig_working_size
    dx = d/(f*o_w);  dy = d/(f*o_h)
    return [
        # Horizontal/vertical moves.
        tlib.Transform(+dx, 0, 1, 0),
        tlib.Transform(-dx, 0, 1, 0),
        tlib.Transform(0, +dy, 1, 0),
        tlib.Transform(0, -dy, 1, 0),

        # Diagonal moves.
        tlib.Transform(+dx, +dy, 1, 0),
        tlib.Transform(-dx, +dy, 1, 0),
        tlib.Transform(+dx, -dy, 1, 0),
        tlib.Transform(-dx, -dy, 1, 0),
    ]


@_floatify_args
def _rot_trs(distance, wsf, orig_working_size):
    # For `distance == 1` we should rotate such that the sides of the image are
    # shifted by one pixel. I.e. theta = 1px/(width/2).
    theta = distance*(180/3.14159)/(wsf*orig_working_size[0]/2)
    return [
        tlib.Transform(0, 0, 1, +theta),
        tlib.Transform(0, 0, 1, -theta),
    ]


@_floatify_args
def _zoom_trs(distance, wsf, orig_working_size):
    # For `distance == 1` we should zoom such that the sides of the image are
    # shifted by one pixel. I.e. factor = (width + 2)/width.
    width = wsf*orig_working_size[0]
    factor = distance*(width + 2)/width
    return [
        tlib.Transform(0, 0, factor, 0),
        tlib.Transform(0, 0, 1/factor, 0),
    ]