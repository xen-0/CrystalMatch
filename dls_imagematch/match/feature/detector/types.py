class DetectorType:
    ORB = "ORB"
    SIFT = "SIFT"
    SURF = "SURF"
    BRISK = "BRISK"
    FAST = "FAST"
    STAR = "STAR"
    MSER = "MSER"
    GFTT = "GFTT"
    HARRIS = "HARRIS"
    DENSE = "Dense"
    BLOB = "SimpleBlob"
    
    LIST_ALL = [ORB, SIFT, SURF, MSER, BRISK, FAST, STAR, GFTT, HARRIS, DENSE, BLOB]
    LIST_FREE = [ORB, BRISK, FAST, STAR, MSER, GFTT, HARRIS, DENSE, BLOB]
    LIST_NON_FREE = [SIFT, SURF]


class ExtractorType:
    # Extractor Types
    ORB = "ORB"
    SURF = "SURF"
    SIFT = "SIFT"
    BRISK = "BRISK"
    BRIEF = "BRIEF"

    LIST_ALL = [ORB, SURF, SIFT, BRIEF, BRISK]

    @staticmethod
    def distance_factor(type):
        """ Each extractor type has a different keypoint representation and so a different metric is used
        for calculating the match keypoint distance in each case. Consequently, the values of keypoint
        distance from two different extractor methods are not directly comparable (e.g. SURF produces
        distances in the range 0-1, whereas SIFT are in the range 100-1000). These distance factors
        bring the distances from each extractor method into roughly the same range (1-100). """
        if type == ExtractorType.ORB:
            return 1
        elif type == ExtractorType.SURF:
            return 100
        elif type == ExtractorType.SIFT:
            return 0.1
        elif type == ExtractorType.BRISK:
            return 0.1
        elif type == ExtractorType.BRIEF:
            return 1


class AdaptationType:
    NONE = ""
    GRID = "Grid"
    PYRAMID = "Pyramid"

    LIST_ALL = [NONE, GRID, PYRAMID]
