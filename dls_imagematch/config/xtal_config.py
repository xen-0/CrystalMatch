from util import Color
from util import Config, IntConfigItem, DirectoryConfigItem, ColorConfigItem, EnumConfigItem, RangeIntConfigItem

from dls_imagematch.match.feature import TransformCalculator
from dls_imagematch.match.feature.detectors import Detector


class XtalConfig(Config):
    def __init__(self, file):
        Config.__init__(self, file)

        add = self.add

        align_detectors = Detector.DETECTOR_TYPES
        align_adaptations = Detector.ADAPTATION_TYPES
        def_detector = Detector.DEFAULT_DETECTOR
        def_adaptation = Detector.DEFAULT_ADAPTATION

        trans_methods = TransformCalculator.METHODS
        trans_filters = TransformCalculator.FILTERS
        def_trans = TransformCalculator.DEFAULT_METHOD
        def_filter = TransformCalculator.DEFAULT_FILTER

        self.color_align = add(ColorConfigItem, "Align Color", Color.Purple())
        self.color_search = add(ColorConfigItem, "Search Box Color", Color.Orange())
        self.color_xtal_img1 = add(ColorConfigItem, "Img1 Xtal Color", Color.Green())
        self.color_xtal_img2 = add(ColorConfigItem, "Img2 Xtal Color", Color.Red())

        self.align_detector = add(EnumConfigItem, "Detector", default=def_detector, extra_arg=align_detectors)
        self.align_adapt = add(EnumConfigItem, "Adaptation", default=def_adaptation, extra_arg=align_adaptations)

        self.region_size = add(IntConfigItem, "Region Size", default=60, extra_arg='px')
        self.search_width = add(IntConfigItem, "Search Width", default=200, extra_arg='px')
        self.search_height = add(IntConfigItem, "Search Height", default=400, extra_arg='px')
        self.transform_method = add(EnumConfigItem, "Transform Method", default=def_trans, extra_arg=trans_methods)
        self.transform_filter = add(EnumConfigItem, "Transform Filter", default=def_filter, extra_arg=trans_filters)

        self.filter_surf = add(RangeIntConfigItem, "SURF Filter", default=30, extra_arg=[1, 100])
        self.filter_sift = add(RangeIntConfigItem, "SIFT Filter", default=25, extra_arg=[1, 100])
        self.filter_orb = add(RangeIntConfigItem, "ORB Filter", default=50, extra_arg=[1, 100])
        self.filter_brief = add(RangeIntConfigItem, "BRIEF Filter", default=50, extra_arg=[1, 100])

        self.input_dir = add(DirectoryConfigItem, "Input Directory", default="../test-images/")
        self.samples_dir = add(DirectoryConfigItem, "Samples Directory", default="../test-images/Sample Sets/")
        self.output_dir = add(DirectoryConfigItem, "Output Directory", default="../test-output/")


        self.initialize_from_file()
