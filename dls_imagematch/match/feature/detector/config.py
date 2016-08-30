from util import Config, IntConfigItem, FloatConfigItem, RangeFloatConfigItem, EnumConfigItem, BoolConfigItem

from .types import DetectorType, ExtractorType
from .detector import Detector
from .detector_orb import OrbDetector
from .detector_sift import SiftDetector
from .detector_surf import SurfDetector
from .detector_mser import MserDetector
from .detector_brisk import BriskDetector


class DetectorConfig:
    def __init__(self, folder):
        self._folder = folder

        self.default = DefaultConfig(folder + "det_default.ini")
        self.orb = OrbConfig(folder + "det_orb.ini")
        self.sift = SiftConfig(folder + "det_sift.ini")
        self.surf = SurfConfig(folder + "det_surf.ini")
        # self.mser = MserConfig(folder + "det_mser.ini")
        self.brisk = BriskConfig(folder + "det_brisk.ini")

    def get_detector_options(self, detector):
        if detector == DetectorType.ORB:
            return self.orb
        elif detector == DetectorType.SIFT:
            return self.sift
        elif detector == DetectorType.SURF:
            return self.surf
        # elif detector == DetectorType.MSER:
        #     return self.mser
        elif detector == DetectorType.BRISK:
            return self.brisk
        else:
            return self.default


class DefaultConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = Detector

        self.set_title("Default Detector Configuration")
        self.set_comment(det.__doc__)

        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)

        self.extractor.set_comment(det.set_extractor.__doc__)

        self.initialize_from_file()


class OrbConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = OrbDetector

        self.set_title("ORB Detector Configuration")
        self.set_comment(det.__doc__)

        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)
        self.n_features = add(IntConfigItem, "Num Features", det.DEFAULT_N_FEATURES)
        self.scale_factor = add(RangeFloatConfigItem, "Scale Factor", det.DEFAULT_SCALE_FACTOR, extra_arg=[1.0, None])
        self.n_levels = add(IntConfigItem, "Num Levels", det.DEFAULT_N_LEVELS)
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", det.DEFAULT_EDGE_THRESHOLD)
        self.first_level = add(IntConfigItem, "First Level", det.DEFAULT_FIRST_LEVEL)
        self.wta_k = add(EnumConfigItem, "WTA_K", det.DEFAULT_WTA_K, det.WTA_K_VALUES)
        self.score_type = add(EnumConfigItem, "Score Type", det.DEFAULT_SCORE_TYPE, det.SCORE_TYPE_NAMES)
        self.patch_size = add(IntConfigItem, "Patch Size", det.DEFAULT_PATCH_SIZE)

        self.extractor.set_comment(det.set_extractor.__doc__)
        self.n_features.set_comment(det.set_n_features.__doc__)
        self.scale_factor.set_comment(det.set_scale_factor.__doc__)
        self.n_levels.set_comment(det.set_n_levels.__doc__)
        self.edge_threshold.set_comment(det.set_edge_threshold.__doc__)
        self.first_level.set_comment(det.set_first_level.__doc__)
        self.wta_k.set_comment(det.set_wta_k.__doc__)
        self.score_type.set_comment(det.set_score_type.__doc__)
        self.patch_size.set_comment(det.set_patch_size.__doc__)

        self.initialize_from_file()


class SiftConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = SiftDetector

        self.set_title("SIFT Detector Configuration")
        self.set_comment(det.__doc__)

        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)
        self.n_features = add(IntConfigItem, "Num Features", det.DEFAULT_N_FEATURES)
        self.n_octave_layers = add(IntConfigItem, "Num Octave Layers", det.DEFAULT_N_OCTAVE_LAYERS)
        self.contrast_threshold = add(FloatConfigItem, "Contrast Threshold", det.DEFAULT_CONTRAST_THRESHOLD)
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", det.DEFAULT_EDGE_THRESHOLD)
        self.sigma = add(FloatConfigItem, "Sigma", det.DEFAULT_SIGMA)

        self.extractor.set_comment(det.set_extractor.__doc__)
        self.n_features.set_comment(det.set_n_features.__doc__)
        self.n_octave_layers.set_comment(det.set_n_octave_layers.__doc__)
        self.contrast_threshold.set_comment(det.set_contrast_threshold.__doc__)
        self.edge_threshold.set_comment(det.set_edge_threshold.__doc__)
        self.sigma.set_comment(det.set_sigma.__doc__)

        self.initialize_from_file()


class SurfConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = SurfDetector

        self.set_title("SURF Detector Configuration")
        self.set_comment(det.__doc__)

        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)
        self.hessian_threshold = add(FloatConfigItem, "Hessian Threshold", det.DEFAULT_HESSIAN_THRESHOLD)
        self.n_octaves = add(IntConfigItem, "Num Octaves", det.DEFAULT_N_OCTAVES)
        self.n_octave_layers = add(IntConfigItem, "Num Octave Layers", det.DEFAULT_N_OCTAVE_LAYERS)
        self.extended = add(BoolConfigItem, "Extended", det.DEFAULT_EXTENDED)
        self.upright = add(BoolConfigItem, "Upright", det.DEFAULT_UPRIGHT)

        self.extractor.set_comment(det.set_extractor.__doc__)
        self.hessian_threshold.set_comment(det.set_hessian_threshold.__doc__)
        self.n_octaves.set_comment(det.set_n_octaves.__doc__)
        self.n_octave_layers.set_comment(det.set_n_octave_layers.__doc__)
        self.extended.set_comment(det.set_extended.__doc__)
        self.upright.set_comment(det.set_upright.__doc__)

        self.initialize_from_file()


class MserConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = MserDetector

        self.set_title("MSER Detector Configuration")
        self.set_comment(det.__doc__)

        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)
        self.delta = add(IntConfigItem, "Delta", det.DEFAULT_DELTA)
        self.min_area = add(IntConfigItem, "Min Area", det.DEFAULT_MIN_AREA)
        self.max_area = add(IntConfigItem, "Max Area", det.DEFAULT_MAX_AREA)
        self.max_variation = add(FloatConfigItem, "Max Variation", det.DEFAULT_MAX_VARIATION)
        self.min_diversity = add(FloatConfigItem, "Min Diversity", det.DEFAULT_MIN_DIVERSITY)
        self.max_evolution = add(IntConfigItem, "Max Evolution", det.DEFAULT_MAX_EVOLUTION)
        self.area_threshold = add(FloatConfigItem, "Area Threshold", det.DEFAULT_AREA_THRESHOLD)
        self.min_margin = add(FloatConfigItem, "Min Margin", det.DEFAULT_MIN_MARGIN)
        self.edge_blur_size = add(IntConfigItem, "Edge Blur Size", det.DEFAULT_EDGE_BLUR_SIZE)

        self.extractor.set_comment(det.set_extractor.__doc__)
        self.delta.set_comment(det.set_delta.__doc__)
        self.min_area.set_comment(det.set_min_area.__doc__)
        self.max_area.set_comment(det.set_max_area.__doc__)
        self.max_variation.set_comment(det.set_max_variation.__doc__)
        self.min_diversity.set_comment(det.set_min_diversity.__doc__)
        self.max_evolution.set_comment(det.set_max_evolution.__doc__)
        self.area_threshold.set_comment(det.set_area_threshold.__doc__)
        self.min_margin.set_comment(det.set_min_margin.__doc__)
        self.edge_blur_size.set_comment(det.set_edge_blur_size.__doc__)

        self.initialize_from_file()


class BriskConfig(Config):
    def __init__(self, file_path):
        Config.__init__(self, file_path)

        add = self.add
        det = BriskDetector

        self.set_title("BRISK Detector Configuration")
        self.set_comment(det.__doc__)

        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)
        self.thresh = add(IntConfigItem, "Threshold", det.DEFAULT_THRESH)
        self.octaves = add(IntConfigItem, "Octaves", det.DEFAULT_OCTAVES)
        self.pattern_scale = add(FloatConfigItem, "Pattern Scale", det.DEFAULT_PATTERN_SCALE)

        self.extractor.set_comment(det.set_extractor.__doc__)
        self.thresh.set_comment(det.set_thresh.__doc__)
        self.octaves.set_comment(det.set_octaves.__doc__)
        self.pattern_scale.set_comment(det.set_pattern_scale.__doc__)

        self.initialize_from_file()
