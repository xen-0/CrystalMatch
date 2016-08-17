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

    def any_matches(self):
        return len(self.matches) > 0

    def has_transform(self):
        return self.transform is not None

    def good_matches(self):
        return [m for m in self.matches if m.is_in_transformation()]

    def num_matches(self):
        return len(self.matches)

    def num_good_matches(self):
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
