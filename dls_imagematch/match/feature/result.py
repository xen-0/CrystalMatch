from __future__ import division


class FeatureMatchResult:
    """ Encapsulates the results of an invocation of the feature matching process. This object is
    returned to the client by FeatureMatcher.
    """
    def __init__(self, img1, img2, matches, transform):
        self.img1 = img1
        self.img2 = img2
        self.matches = matches
        self.transform = transform

        self.method = None
        self.method_adapt = None

        self.coherence = self._calculate_coherence()

    def any_matches(self):
        return len(self.matches) > 0

    def has_transform(self):
        return self.transform is not None

    def _calculate_coherence(self):

        good_matches = [m for m in self.matches if m.is_in_transformation()]
        distances = [m.reprojection_error() for m in good_matches]

        if len(good_matches) == 0:
            return 0

        total = sum(distances) / len(good_matches)
        print("Coherence: {:.3f}".format(total))
        return total
