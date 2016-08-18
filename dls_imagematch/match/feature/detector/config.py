from util import Config, IntConfigItem, RangeFloatConfigItem, EnumConfigItem

from .detector_orb import OrbDetector


class DetectorConfig:
    def __init__(self, folder):
        self._folder = folder

        self.orb = OrbConfig(folder + "orb.ini")


class OrbConfig(Config):
    def __init__(self, filepath):
        Config.__init__(self, filepath)

        add = self.add
        od = OrbDetector

        self.n_features = add(IntConfigItem, "Num Features", od.DEFAULT_N_FEATURES)
        self.scale_factor = add(RangeFloatConfigItem, "Scale Factor", od.DEFAULT_SCALE_FACTOR, extra_arg=[1.0, None])
        self.n_levels = add(IntConfigItem, "Num Levels", od.DEFAULT_N_LEVELS)
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", od.DEFAULT_EDGE_THRESHOLD)
        self.first_level = add(IntConfigItem, "First Level", od.DEFAULT_FIRST_LEVEL)
        self.wta_k = add(EnumConfigItem, "WTA_K", od.DEFAULT_WTA_K, od.WTA_K_VALUES)
        self.score_type = add(EnumConfigItem, "Score Type", od.DEFAULT_SCORE_TYPE, od.SCORE_TYPE_NAMES)
        self.orb_patch_size = add(IntConfigItem, "Patch Size", od.DEFAULT_PATCH_SIZE)
