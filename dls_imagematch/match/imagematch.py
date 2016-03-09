from copy import deepcopy
from functools import reduce
from itertools import product
from operator import add

import cv2
import numpy as np

import dls_imagematch.util.transforms as tlib  # Contains `Transform` class.
from dls_imagematch.match.image import Image
from dls_imagematch.match.metric import OverlapMetric
from dls_imagematch.match.trials import TrialTransforms
from dls_imagematch.util.parallelmap import parallel_map
from dls_imagematch.util.setutils import agreeing_subset_indices


class ImageMatcher:

    def __init__(self):
        # Scale factor for earlier matching iterations
        self._scale_factors = (0.25, 0.5, 1) # Used to include 0.125
        # Scale-dependent range of frequencies to pick out in preprocessing step
        self._freq_range = (1, 50)
        # Consider only translations (no rot/scale)?
        self._translation_only = True
        # Use consensus algorithm
        self._use_consensus = False
        # Number of separate process to use in consensus matching
        self._num_processes = 8
        # Display debug data and progress images during run
        self.DEBUG = False

    def set_debug(self, debug=True):
        self.DEBUG = debug

    def set_consensus(self, consensus):
        self._use_consensus = consensus

    def match(self, reference_img, move_img, guess):
        if self._use_consensus:
            return self._match_consensus(reference_img, move_img)
        else:
            return self._match_single(reference_img, move_img, guess)


    def _match_single(self, img_ref, img_mov, guess):
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
        # What return value do we expect? (Speed up the program by guessing well.)
        net_transform = guess

        for scale in self._scale_factors:
            # The transformations applied must be made relative to the current scale factor
            mov_original_size = img_mov.size
            mov_scaled_size = (mov_original_size[0] * scale, mov_original_size[1] * scale)

            # Do the scale factor-dependent preprocessing step. In our case, we'll
            # pick out frequency ranges somewhat coarser than 1 px. Then resize the
            # image to the correct scale
            scale_img_ref = img_ref.freq_range(self._freq_range, scale).rescale(scale)
            scale_img_mov = img_mov.freq_range(self._freq_range, scale).rescale(scale)

            # Metric calculator which determines how good of a match a given transformation is
            metric_calc = OverlapMetric(scale_img_ref, scale_img_mov, self._translation_only)
            metric_calc.DEBUG = self.DEBUG

            # Choose the transform candidates for this working size.
            trial_transforms = TrialTransforms(mov_original_size)
            trial_transforms.add_kings(1, scale)
            trial_transforms.add_kings(2, scale)

            if not self._translation_only:
                pass #trial_transforms.a

            # Perform the metric minimisation
            min_reached = False
            while not min_reached:
                net_transform, best_img, min_reached = \
                    metric_calc.best_transform(trial_transforms, mov_scaled_size, net_transform)

                if self.DEBUG:
                    print('(wsf:{})'.format(scale))
                    #img = cv2.resize(best_img/float(np.max(best_img)), (0, 0), fx=1/scale, fy=1/scale)
                    img = cv2.resize(best_img, (0, 0), fx=1/scale, fy=1/scale)
                    cv2.imshow('progress', img)
                    cv2.waitKey(0)

        # TODO: Return a weighted average of the best transforms (i.e. subpixel).
        return net_transform


    def _match_consensus(self, ref, img, **kwargs):
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
        trs = parallel_map(self._num_processes, self._match_single, arg_list)

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
