from functools import partial, reduce
from itertools import product
from copy import deepcopy
from operator import add

import cv2
import numpy as np

import dls_imagematch.transforms as tlib  # Contains `Transform` class.
from .parallelmap import parallel_map
from .setutils import agreeing_subset_indices

from .image import Image
from .imagemetric import ImageMetric

def find_tr(
        img_ref, img_mov,  # Reference and translated images.
        translation_only=True,  # Consider only translations (no rot/scale)?
        freq_range=(1, 50),  # Scale-dep. preproc..
        guess=tlib.Transform.identity(),  # Expected transform.
        wsfs=(0.125, 0.25, 0.5, 1),  # Working size factors.
        crop_amounts=[0.1]*4,  # Edge regions to exclude from metric.
        debug=False,  # Display progress?
    ):
    """Return (hopefully) the `Transform` which maps `img` onto `ref_img`.

    How does this function work? Answer:

    It tries applying a bunch of slightly different affine transforms to the
    overlaid image and keeps the one which minimises a metric. It repeats
    this process until it has found a local minimum in the metric.

    That's not the whole story. For the first iterations, the two images are
    scaled down by a factor of 8. The function proceeds as usual until it
    finds a local minimum to the nearest pixel in x and y. At this point, the
    two images are blown up by a factor of two (to a net scale factor of 1/4)
    and again the function finds a local minimum to the nearest pixel in x
    and y. This process is repeated at scale factors 1/2 and finally 1.

    By taking this approach (starting coarse and gradually getting finer) the
    function runs quicker than if it worked at scale factor 1 the whole time.
    This is because the cost of computing the metric scales with image area.
    Furthermore, a preprocessing operation may be invoked on the images at
    each rescaling, which can pick out coarser or finer image features at
    a given scale factor. This might work better than using all image
    features at every stage. In practice, it does seem that this is an
    important feature of the algorithm. Most importantly, when doing the
    precision matching at scale factor 1, picking out a set of high-frequency
    components ignores low-frequency variation between the images --
    typically the result of differences in lighting conditions.

    At each scale factor the function uses a different set of candidate
    transforms. Typically, transform amounts should correspond to
    translations of a single pixel at the given scale factor.

    Optionally, the function could work to a greater precision than "nearest-
    pixel", since OpenCV uses anti-aliasing when applying affine transforms.
    This might also allow for speed improvements.

    For performance reasons, this function uses implementation details of the
    `Transform` class. It's cheaper to manually keep track of the matrix
    forms of affine transforms, than to compose many `Transform` objects with
    `__mul__` and then execute `__call__` every time we want to obtain their
    matrix forms.
    """

    # DEBUG
    img_ref, img_mov = Image(img_ref), Image(img_mov)

    # What return value do we expect? (Speed up the program by guessing well.)
    net_tr = guess

    orig_size = img_mov.size()

    for wsf in wsfs:  # Working size factors.
        new_size = tuple(map(int, map(lambda x: x*wsf, orig_size)))
        # Refresh the net transform matrix for the new working size.
        # (Remember that the matrix representation of a given `Transform`
        # object depends on the working size.)
        net_tr_mat = net_tr(new_size)

        # Do the scale factor-dependent preprocessing step. In our case, we'll
        # pick out frequency ranges somewhat coarser than 1 px.
        freq_img_ref = img_ref.pick_frequency_range(freq_range, wsf)
        freq_img_mov = img_mov.pick_frequency_range(freq_range, wsf)

        # Rescale the preprocessed images
        scale_img_ref = freq_img_ref.resize(new_size)
        scale_img_mov = freq_img_mov.resize(new_size)

        # Metric calculator which determines how goof of a match a given transformation is
        metric_calc = ImageMetric(scale_img_ref, scale_img_mov, crop_amounts, translation_only)

        # Choose the transform candidates for this working size.
        trs = [tlib.Transform.identity()]
        trs.extend(_king_trs(1, wsf, orig_size))
        trs.extend(_king_trs(2, wsf, orig_size))
        if not translation_only:
            pass  # TODO: Add some zoom, rot transforms here.

        best = None  # Which fresh transform candidate minimises the metric?
        while 0 != best:  # While it's not the identity transform...

            # Randomize the random transforms (if any -- none presently).
            fresh_trs = [tr() if isinstance(tr, tlib.RandomTransformer)
                         else tr for tr in trs]

            # Compose the new transform candidates with the old net transform.
            net_trs = [fresh_tr * net_tr for fresh_tr in fresh_trs]

            # Do the work of turning the new `Transform`s into matrices here.
            # Else it would be left to `apply_tr` to do expensively.
            net_tr_mats = [
                tlib.Transform._compose_matrix_forms(
                    fresh_tr(new_size), net_tr_mat)
                for fresh_tr in fresh_trs]

            # Evaluate the metric for each transform.
            metric_imgs = list(map(metric_calc.get_absdiff_metric_image, net_tr_mats))
            metrics = list(map(np.sum, metric_imgs))

            # Choose the net transform which minimises the metric.
            best = np.argmin(metrics)
            net_tr = net_trs[best]
            net_tr_mat = net_tr_mats[best]

            if debug:
                print('(wsf:{}) {}'.format(wsf,metrics))

                cv2.imshow(
                    'progress',
                    cv2.resize(
                        metric_imgs[best]/float(np.max(metric_imgs[best])),
                        (0, 0), fx=1/wsf, fy=1/wsf))
                cv2.waitKey(0)


    # TODO: Return a weighted average of the best transforms (i.e. subpixel).
    return net_tr


def find_consensus_tr(n_processes, ref, img, **kwargs):
    """Apply `find_tr` with few guesses and return the consensus `Transform`.

    `kwargs` are passed directly to `find_tr`, apart from `guess` and `debug`
    which are overridden.

    Currently, consensus finding is only implemented for translations
    (no rot/scale).
    """
    # TODO: Add meta-guess.
    guesses = map(lambda x, y: tlib.Transform.translation(*(x, y)),
                  product((-0.06, 0.06), (-0.1, -0.03, 0.03, 0.1)))

    # Construct a list of argument tuples to pass to `parallel_map`.
    arg_list = (((ref, img), updated(kwargs, {'guess': guess, 'debug': False}))
                for guess in guesses)

    # Dispatch `find_tr` to multiple cores and collect the results.
    trs = parallel_map(n_processes, find_tr, arg_list)

    # Get information from transforms for purposes of consensus finding.
    tr_mats = map(lambda tr: tr(get_size(ref)), trs)
    translations = map(get_translation_amounts, tr_mats)

    # How similar must points be to "agree"?
    consensus_distance = 2  # Pixels.

    # Find internally agreeing sets of translations.
    translation_sets = list(agreeing_subset_indices(
        translations,
        lambda p, o: distance(p, o) < consensus_distance))

    # Which internally agreeing set has the most members?
    set_lengths = map(len, translation_sets)
    consensus = np.argmax(set_lengths)  # TODO: Check if tied for longest.

    # Choose an arbitrary transform from the consensus group.
    best = list(translation_sets[consensus])[0]

    print('Confidence:', str(set_lengths[consensus])+'/'+str(len(guesses)))

    return trs[best]


def get_translation_amounts(tr_mat):
    return map(lambda i: tr_mat[i, 2], (0, 1))


def get_size(img):
    """Return the size of an image in pixels in the format [width, height]."""
    if img.ndim == 3:  # Colour
        working_size = img.shape[::-1][1:3]
    else:
        assert img.ndim == 2  # Greyscale
        working_size = img.shape[::-1]
    return working_size


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


def distance(point_a, point_b):
    """Return the distance between two points in n-dim Euclidean space.
    """
    quadrature_add = lambda *args: np.sqrt(reduce(add, (a*a for a in args)))
    return quadrature_add(*np.subtract(point_a, point_b))


def updated(orig_dict, update_dict):
    """Pure functional dict update.
    """
    copy = deepcopy(orig_dict)
    copy.update(update_dict)
    return copy
