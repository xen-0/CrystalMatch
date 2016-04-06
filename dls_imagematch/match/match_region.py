from __future__ import division

from dls_imagematch.match.metric_overlap import OverlapMetric
from dls_imagematch.match.trials import TrialTransforms


class RegionMatcher:
    def __init__(self, reference_img, moving_img, starting_guess, scales=(0.25, 0.5, 1)):
        # Scale factor for earlier matching iterations
        self._scale_factors = scales # Used to include 0.125
        # Scale-dependent range of frequencies to pick out in preprocessing step
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
        if not self.match_complete:
            self._next_iteration()

        return self.net_transform

    def skip_to_next_scale(self):
        current_scale = self._scale

        while not self.match_complete and self._scale == current_scale:
            self._next_iteration()

        return self.net_transform

    def skip_to_end(self):
        while not self.match_complete:
            self._next_iteration()

        return self.net_transform

    def _next_scale_factor(self):
        if self._scale == self._scale_factors[-1]:
            self.match_complete = True
        else:
            self._scale_index += 1
            self._scale = self._scale_factors[self._scale_index]
            self._initialize_scale_factor(self._scale)


    def _initialize_scale_factor(self, scale):
        # Do the scale factor-dependent preprocessing step. In our case, we'll
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

    def _next_iteration(self):
        self._iteration += 1

        scaled_transform = self.net_transform.scale(self._scale)

        scaled_transform, min_reached = \
            self._metric_calc.best_transform(scaled_transform)

        self.net_transform = scaled_transform.scale(1/self._scale)

        if min_reached:
            self._next_scale_factor()


    '''
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
            metric_calc = OverlapMetric(scale_img_ref, scale_img_mov, True)

            # Choose the transform candidates for this working size.
            trial_transforms = TrialTransforms(mov_original_size)
            trial_transforms.add_kings(1, scale)
            trial_transforms.add_kings(2, scale)

            # Perform the metric minimisation
            min_reached = False
            while not min_reached:
                net_transform, best_img, min_reached = \
                    metric_calc.best_transform(trial_transforms, mov_scaled_size, net_transform)

                if self.DEBUG:
                    print('(wsf:{})'.format(scale))
                    img = cv2.resize(best_img, (0, 0), fx=1/scale, fy=1/scale)
                    cv2.imshow('progress', img)
                    cv2.waitKey(0)

        # TODO: Return a weighted average of the best transforms (i.e. subpixel).
        return net_transform
    '''
