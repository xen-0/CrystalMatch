from dls_imagematch.feature.detector.types import DetectorType
from dls_util.config import Config, IntConfigItem, DirectoryConfigItem, EnumConfigItem


class FocusConfig(Config):
    def __init__(self, file):
        Config.__init__(self, file)

        add = self.add

        methods = DetectorType.LIST_FREE

        self.align_method = add(EnumConfigItem, "Alignment Method", default="SURF", extra_arg=methods)
        self.kernel_size = add(IntConfigItem, "Laplacian Kernel Size", default=5, extra_arg='px')
        self.blur_radius = add(IntConfigItem, "Laplacian Blur Radius", default=5, extra_arg='px')
        self.input_dir = add(DirectoryConfigItem, "Input Directory", default="../test-images/Focus Stacking/VMXI-AA005-G07-1-R0DRP1")
        self.output_dir = add(DirectoryConfigItem, "Output Directory", default="../test-output/focus/")

        self.initialize_from_file()
