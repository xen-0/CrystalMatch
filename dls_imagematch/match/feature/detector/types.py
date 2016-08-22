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
    
    LIST_ALL = [ORB, SIFT, SURF, BRISK, FAST, STAR, MSER, GFTT, HARRIS, DENSE, BLOB]
    LIST_FREE = [ORB, BRISK, FAST, STAR, MSER, GFTT, HARRIS, DENSE, BLOB]
    LIST_NON_FREE = [SIFT, SURF]


class ExtractorType:
    # Extractor Types
    ORB = "ORB"
    SURF = "SURF"
    SIFT = "SIFT"
    BRIEF = "BRIEF"

    LIST_ALL = [ORB, SURF, SIFT, BRIEF]


class AdaptationType:
    NONE = ""
    GRID = "Grid"
    PYRAMID = "Pyramid"

    LIST_ALL = [NONE, GRID, PYRAMID]
