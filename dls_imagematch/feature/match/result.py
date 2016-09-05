from __future__ import division


class FeatureMatcherResult:
    """ Encapsulates the results of an invocation of the feature matching process. This object is
    returned to the client by FeatureMatcher.
    """
    def __init__(self, img1, img2, matches, transform, method):
        self._img1 = img1
        self._img2 = img2
        self._matches = matches
        self._transform = transform
        self._method = method

    def img1(self): return self._img1

    def img2(self): return self._img2

    def matches(self): return self._matches

    def transform(self): return self._transform

    def method(self): return self._method

    def any_matches(self):
        """ True if the result contains any feature matches. """
        return len(self._matches) > 0

    def num_matches(self):
        """ The number of feature matches (whether good or bad). """
        return len(self._matches)

    def has_transform(self):
        """ True if a transformation was successfully calculated from the feature matches. """
        return self._transform is not None

    def good_matches(self):
        """ Returns the list of matches that were included in the transformation calculation. """
        return [m for m in self._matches if m.is_in_transformation()]

    def num_good_matches(self):
        """ The number of good feature matches. """
        return len(self.good_matches())

    def mean_transform_error(self):
        """ Calculates the average reprojection error of all the good matches (those involved
        in calculating the transformation)."""
        good_matches = self.good_matches()
        if len(good_matches) == 0:
            return 0

        errors = [m.reprojection_error() for m in good_matches]
        total = sum(errors) / len(good_matches)
        return total
