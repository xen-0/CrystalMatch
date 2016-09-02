from dls_imagematch.util import Config, IntConfigItem, RangeIntConfigItem,\
    FloatConfigItem, RangeFloatConfigItem, EnumConfigItem, BoolConfigItem

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

    def get_default_options(self):
        return self.default

    def is_detector_enabled(self, detector):
        """ Returns true if the detector is enabled. Takes into account whether the detector is non-free and if
        non-free detectors are disabled. """
        options = self.get_detector_options(detector)
        is_enabled = options.enabled.value()

        if is_enabled:
            default = self.get_default_options()
            is_non_free = DetectorType.is_non_free(detector)
            if is_non_free and not default.use_non_free.value():
                is_enabled = False

        return is_enabled

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


class _BaseDetectorConfig(Config):
    def __init__(self, file_path, detector_type):
        Config.__init__(self, file_path)

        add = self.add
        det = detector_type

        self.enabled = add(BoolConfigItem, "Enabled", default=det.DEFAULT_ENABLED)
        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)
        self.keypoint_limit = add(RangeIntConfigItem, "Keypoint Limit", det.DEFAULT_KEYPOINT_LIMIT, [1, 100])

        self.enabled.set_comment(det.set_enabled.__doc__)
        self.extractor.set_comment(det.set_extractor.__doc__)
        self.keypoint_limit.set_comment(det.set_keypoint_limit.__doc__)


class DefaultConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, Detector)

        add = self.add
        det = Detector

        self.set_title("Default Detector Configuration")
        self.set_comment(det.__doc__)

        self.use_non_free = add(BoolConfigItem, "Non-Free Algorithms", default=True)
        self.use_non_free.set_comment("Use proprietary algorithms (SIFT and SURF) in matching.")

        self.initialize_from_file()


class OrbConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, OrbDetector)

        add = self.add
        det = OrbDetector

        self.set_title("ORB Detector Configuration")
        self.set_comment(det.__doc__)

        self.n_features = add(IntConfigItem, "Num Features", det.DEFAULT_N_FEATURES, [1, None])
        self.scale_factor = add(RangeFloatConfigItem, "Scale Factor", det.DEFAULT_SCALE_FACTOR, [1.001, None])
        self.n_levels = add(RangeIntConfigItem, "Num Levels", det.DEFAULT_N_LEVELS, [1, None])
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", det.DEFAULT_EDGE_THRESHOLD, [1, None])
        self.first_level = add(RangeIntConfigItem, "First Level", det.DEFAULT_FIRST_LEVEL, [0, 0])
        self.wta_k = add(EnumConfigItem, "WTA_K", det.DEFAULT_WTA_K, det.WTA_K_VALUES)
        self.score_type = add(EnumConfigItem, "Score Type", det.DEFAULT_SCORE_TYPE, det.SCORE_TYPE_NAMES)
        self.patch_size = add(IntConfigItem, "Patch Size", det.DEFAULT_PATCH_SIZE, [2, None])

        self.n_features.set_comment(det.set_n_features.__doc__)
        self.scale_factor.set_comment(det.set_scale_factor.__doc__)
        self.n_levels.set_comment(det.set_n_levels.__doc__)
        self.edge_threshold.set_comment(det.set_edge_threshold.__doc__)
        self.first_level.set_comment(det.set_first_level.__doc__)
        self.wta_k.set_comment(det.set_wta_k.__doc__)
        self.score_type.set_comment(det.set_score_type.__doc__)
        self.patch_size.set_comment(det.set_patch_size.__doc__)

        self.initialize_from_file()


class SiftConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, SiftDetector)

        add = self.add
        det = SiftDetector

        self.set_title("SIFT Detector Configuration")
        self.set_comment(det.__doc__)

        self.n_features = add(RangeIntConfigItem, "Num Features", det.DEFAULT_N_FEATURES, [1, None])
        self.n_octave_layers = add(RangeIntConfigItem, "Num Octave Layers", det.DEFAULT_N_OCTAVE_LAYERS, [1, None])
        self.contrast_threshold = add(FloatConfigItem, "Contrast Threshold", det.DEFAULT_CONTRAST_THRESHOLD)
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", det.DEFAULT_EDGE_THRESHOLD)
        self.sigma = add(FloatConfigItem, "Sigma", det.DEFAULT_SIGMA)

        self.n_features.set_comment(det.set_n_features.__doc__)
        self.n_octave_layers.set_comment(det.set_n_octave_layers.__doc__)
        self.contrast_threshold.set_comment(det.set_contrast_threshold.__doc__)
        self.edge_threshold.set_comment(det.set_edge_threshold.__doc__)
        self.sigma.set_comment(det.set_sigma.__doc__)

        self.initialize_from_file()


class SurfConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, SurfDetector)

        add = self.add
        det = SurfDetector

        self.set_title("SURF Detector Configuration")
        self.set_comment(det.__doc__)

        self.hessian_threshold = add(RangeFloatConfigItem, "Hessian Threshold", det.DEFAULT_HESSIAN_THRESHOLD, [0.0, None])
        self.n_octaves = add(RangeIntConfigItem, "Num Octaves", det.DEFAULT_N_OCTAVES, [0, None])
        self.n_octave_layers = add(RangeIntConfigItem, "Num Octave Layers", det.DEFAULT_N_OCTAVE_LAYERS, [1, None])
        self.extended = add(BoolConfigItem, "Extended", det.DEFAULT_EXTENDED)
        self.upright = add(BoolConfigItem, "Upright", det.DEFAULT_UPRIGHT)

        self.hessian_threshold.set_comment(det.set_hessian_threshold.__doc__)
        self.n_octaves.set_comment(det.set_n_octaves.__doc__)
        self.n_octave_layers.set_comment(det.set_n_octave_layers.__doc__)
        self.extended.set_comment(det.set_extended.__doc__)
        self.upright.set_comment(det.set_upright.__doc__)

        self.initialize_from_file()


class MserConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, MserDetector)

        add = self.add
        det = MserDetector

        self.set_title("MSER Detector Configuration")
        self.set_comment(det.__doc__)

        self.delta = add(IntConfigItem, "Delta", det.DEFAULT_DELTA)
        self.min_area = add(IntConfigItem, "Min Area", det.DEFAULT_MIN_AREA)
        self.max_area = add(IntConfigItem, "Max Area", det.DEFAULT_MAX_AREA)
        self.max_variation = add(FloatConfigItem, "Max Variation", det.DEFAULT_MAX_VARIATION)
        self.min_diversity = add(FloatConfigItem, "Min Diversity", det.DEFAULT_MIN_DIVERSITY)
        self.max_evolution = add(IntConfigItem, "Max Evolution", det.DEFAULT_MAX_EVOLUTION)
        self.area_threshold = add(FloatConfigItem, "Area Threshold", det.DEFAULT_AREA_THRESHOLD)
        self.min_margin = add(FloatConfigItem, "Min Margin", det.DEFAULT_MIN_MARGIN)
        self.edge_blur_size = add(IntConfigItem, "Edge Blur Size", det.DEFAULT_EDGE_BLUR_SIZE)

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


class BriskConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, BriskDetector)

        add = self.add
        det = BriskDetector

        self.set_title("BRISK Detector Configuration")
        self.set_comment(det.__doc__)

        self.thresh = add(RangeIntConfigItem, "Threshold", det.DEFAULT_THRESH, [0, None])
        self.octaves = add(RangeIntConfigItem, "Octaves", det.DEFAULT_OCTAVES, [0, None])
        self.pattern_scale = add(RangeFloatConfigItem, "Pattern Scale", det.DEFAULT_PATTERN_SCALE, [0.0, None])

        self.thresh.set_comment(det.set_thresh.__doc__)
        self.octaves.set_comment(det.set_octaves.__doc__)
        self.pattern_scale.set_comment(det.set_pattern_scale.__doc__)

        self.initialize_from_file()
