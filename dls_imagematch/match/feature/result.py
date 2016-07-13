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

    def calculate_coherence(self):

        good_matches = [m for m in self.matches if m.is_in_transformation()]

        total = 0
        distances = []
        for match in good_matches:
            point1 = match.point1()
            point2 = match.point2()
            projected_point2 = self.transform.transform_points([point1])[0]
            distance = point2.distance_to(projected_point2)
            distances.append(distance)

        total = sum(distances) / len(good_matches)
        print("Coherence: {:.3f}".format(total))
        print(sorted(distances))
        return total
