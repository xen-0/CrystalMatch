from __future__ import division

from dls_imagematch.match.metric_overlap import OverlapMetric
from dls_imagematch.match.trials import TrialTransforms


class RegionMatcher:
    """ This class performs region matching to compare two images and align the second one to the first.

    We define a metric (implemented by another class) that calculates how good of a 'match' the second
    image is to the first when it is overlaid on top of it at a given offset. In this case the metric
    quantifies the average of the differences in the brightness of the overlaid pixels.

    This class is essentially a minimisation routine over an integer space (the grid of pixels). From
    our initial starting position, we attempt to move to a position that minimises the value of the metric.
    At each iteration, we calculate the value of the metric at the current position, at a surrounding
    positions. We move to the position with the minimum metric value and start the next iteration. We keep
    going in this fashion until we reach a local minimum, at which point the procedure stops.

    If our starting guess is reasonably close to the actual 'match' position, then we should usually end up
    with the optimum fit, though this is not guaranteed. If the starting position is far from the 'match'
    position, then there is a good chance that the procedure will get trapped in a local minimum.

    As an improvement to the speed (and accuracy), we run the procedure at a range of different scale
    factors. We first scale the images down (by e.g. a factor of 4), so that they are much smaller, and
    then run the process on these resized images, we then scale the image up and run it again (taking the
    final position from the smaller scale image as the starting point for the larger scale). We keep doing
    this until we reach the original image scale.

    Furthermore, a pre-processing operation may be invoked on the images at  each rescaling, which can pick
    out coarser or finer image features at a given scale factor. This might work better than using all image
    features at every stage. In practice, it does seem that this is an important feature of the algorithm.
    Most importantly, when doing the precision matching at scale factor 1, picking out a set of high-frequency
    components ignores low-frequency variation between the images -- typically the result of differences in
    lighting conditions.

    The matching procedure can be advanced a single iteration at a time by the client code. This makes it easier
    to visually demonstrate the matching process.
    """
    def __init__(self, reference_img, moving_img, starting_guess, scales=(0.25, 0.5, 1)):
        # Scale factor for earlier matching iterations
        self._scale_factors = scales  # Used to include 0.125
        # Scale-dependent range of frequencies to pick out in pre-processing step
        self._freq_range = (1, 50)

        self.img_a = reference_img
        self.img_b = moving_img
        self.net_transform = starting_guess

        self.match_complete = False

        self._iteration = -1
        self._scale = 0
        self._scale_index = -1
        self._metric_calc = None

        self._next_scale_factor()

    def next_frame(self):
        """ Perform the next single iteration of the matching procedure. """
        if not self.match_complete:
            self._next_iteration()

        return self.net_transform

    def skip_to_next_scale(self):
        """ Keep performing iterations until the next scale factor is reached. """
        current_scale = self._scale

        while not self.match_complete and self._scale == current_scale:
            self._next_iteration()

        return self.net_transform

    def skip_to_end(self):
        """ Keep performing iterations until the matching procedure is complete. """
        while not self.match_complete:
            self._next_iteration()

        return self.net_transform

    def _next_iteration(self):
        """ Perform the next iteration of the matching procedure; move to the next scale factor if
        we've reached the minimum, or declare complete if we are at the original image size. """
        self._iteration += 1

        scaled_transform = self.net_transform.scale(self._scale)

        scaled_transform, min_reached = \
            self._metric_calc.best_transform(scaled_transform)

        self.net_transform = scaled_transform.scale(1/self._scale)

        if min_reached:
            self._next_scale_factor()

    def _next_scale_factor(self):
        """ Prepare images for the next scale factor (or declare complete. """
        if self._scale == self._scale_factors[-1]:
            self.match_complete = True
        else:
            self._scale_index += 1
            self._scale = self._scale_factors[self._scale_index]
            self._initialize_scale_factor(self._scale)

    def _initialize_scale_factor(self, scale):
        """ Prepare the images (re-size and pre-processing) for the specified scale factor. """
        # Do the scale factor-dependent pre-processing step. In our case, we'll
        # pick out frequency ranges somewhat coarser than 1 px. Then resize the
        # image to the correct scale
        scale_img_ref = self.img_a.freq_range(self._freq_range, scale).rescale(scale)
        scale_img_mov = self.img_b.freq_range(self._freq_range, scale).rescale(scale)

        # Choose the transform candidates for this working size.
        trial_transforms = TrialTransforms()
        trial_transforms.add_kings(1)
        trial_transforms.add_kings(2)

        # Metric calculator which determines how good of a match a given transformation is
        self._metric_calc = OverlapMetric(scale_img_ref, scale_img_mov, trial_transforms)
