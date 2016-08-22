from util import Config, IntConfigItem, FloatConfigItem, RangeFloatConfigItem, EnumConfigItem, BoolConfigItem

from .types import DetectorType
from .detector_orb import OrbDetector
from .detector_sift import SiftDetector
from .detector_surf import SurfDetector
from .detector_mser import MserDetector


class DetectorConfig:
    def __init__(self, folder):
        self._folder = folder

        self.orb = OrbConfig(folder + "det_orb.cfg")
        self.sift = SiftConfig(folder + "det_sift.cfg")
        self.surf = SurfConfig(folder + "det_surf.cfg")
        self.mser = MserConfig(folder + "det_mser.cfg")

    def get_detector_options(self, detector):
        if detector == DetectorType.ORB:
            return self.orb
        elif detector == DetectorType.SIFT:
            return self.sift
        elif detector == DetectorType.SURF:
            return self.surf
        elif detector == DetectorType.MSER:
            return self.mser

        return None


class OrbConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = OrbDetector

        self.n_features = add(IntConfigItem, "Num Features", det.DEFAULT_N_FEATURES)
        self.scale_factor = add(RangeFloatConfigItem, "Scale Factor", det.DEFAULT_SCALE_FACTOR, extra_arg=[1.0, None])
        self.n_levels = add(IntConfigItem, "Num Levels", det.DEFAULT_N_LEVELS)
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", det.DEFAULT_EDGE_THRESHOLD)
        self.first_level = add(IntConfigItem, "First Level", det.DEFAULT_FIRST_LEVEL)
        self.wta_k = add(EnumConfigItem, "WTA_K", det.DEFAULT_WTA_K, det.WTA_K_VALUES)
        self.score_type = add(EnumConfigItem, "Score Type", det.DEFAULT_SCORE_TYPE, det.SCORE_TYPE_NAMES)
        self.patch_size = add(IntConfigItem, "Patch Size", det.DEFAULT_PATCH_SIZE)

        self.initialize_from_file()


class SiftConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = SiftDetector

        self.n_features = add(IntConfigItem, "Num Features", det.DEFAULT_N_FEATURES)
        self.n_octave_layers = add(IntConfigItem, "Num Octave Layers", det.DEFAULT_N_OCTAVE_LAYERS)
        self.contrast_threshold = add(FloatConfigItem, "Contrast Threshold", det.DEFAULT_CONTRAST_THRESHOLD)
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", det.DEFAULT_EDGE_THRESHOLD)
        self.sigma = add(FloatConfigItem, "Sigma", det.DEFAULT_SIGMA)

        self.initialize_from_file()


class SurfConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = SurfDetector

        self.hessian_threshold = add(FloatConfigItem, "Hessian Threshold", det.DEFAULT_HESSIAN_THRESHOLD)
        self.n_octaves = add(IntConfigItem, "Num Octaves", det.DEFAULT_N_OCTAVES)
        self.n_octave_layers = add(IntConfigItem, "Num Octave Layers", det.DEFAULT_N_OCTAVE_LAYERS)
        self.extended = add(BoolConfigItem, "Extended", det.DEFAULT_EXTENDED)
        self.upright = add(BoolConfigItem, "Upright", det.DEFAULT_UPRIGHT)

        self.initialize_from_file()


class MserConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = MserDetector

        self.delta = add(IntConfigItem, "Delta", det.DEFAULT_DELTA)
        self.min_area = add(IntConfigItem, "Min Area", det.DEFAULT_MIN_AREA)
        self.max_area = add(IntConfigItem, "Max Area", det.DEFAULT_MAX_AREA)
        self.max_variation = add(FloatConfigItem, "Max Variation", det.DEFAULT_MAX_VARIATION)
        self.min_diversity = add(FloatConfigItem, "Min Diversity", det.DEFAULT_MIN_DIVERSITY)
        self.max_evolution = add(IntConfigItem, "Max Evolution", det.DEFAULT_MAX_EVOLUTION)
        self.area_threshold = add(FloatConfigItem, "Area Threshold", det.DEFAULT_AREA_THRESHOLD)
        self.min_margin = add(FloatConfigItem, "Min Margin", det.DEFAULT_MIN_MARGIN)
        self.edge_blur_size = add(IntConfigItem, "Edge Blur Size", det.DEFAULT_EDGE_BLUR_SIZE)

        self.initialize_from_file()
