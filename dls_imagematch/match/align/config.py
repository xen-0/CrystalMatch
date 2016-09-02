from feature.detector import DetectorType
from dls_imagematch.util.config import Config, EnumConfigItem, BoolConfigItem


class AlignConfig(Config):
    """ Configuration class that contains a number of options for the program. Stores options in a config
    file that can be edited externally to set the values of the options.
    """
    def __init__(self, config_directory):
        Config.__init__(self, config_directory + "align.ini")

        add = self.add

        self.set_title("Image Alignment Configuration")
        self.set_comment("Configuration for the initial image alignment process used in the crystal matching")

        self.use_alignment = add(BoolConfigItem, "Perform Alignment", True)
        self.use_alignment.set_comment("Automatically perform bulk image alignment when a new image is selected.")

        self.align_detector = add(EnumConfigItem, "Detector", default=DetectorType.ORB, extra_arg=DetectorType.LIST_ALL)
        self.align_detector.set_comment("Feature detection algorithm to be used for the initial image alignment "
                                        "process.")

        self.initialize_from_file()
