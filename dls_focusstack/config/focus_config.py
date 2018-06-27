from dls_util.config.config import Config
from dls_util.config.item import IntConfigItem


class FocusConfig(Config):
    def __init__(self, filename):
        Config.__init__(self, filename)

        add = self.add

        self.kernel_size = add(IntConfigItem, "Laplacian Kernel Size", default=5, extra_arg='px')
        self.blur_radius = add(IntConfigItem, "Laplacian Blur Radius", default=5, extra_arg='px')
        self.pyramid_min_size = add(IntConfigItem, "Pyramid Minimum Size", default=32, extra_arg='px') #defalt =32

        #self.input_dir = add(DirectoryConfigItem, "In Directory",)

        self.initialize_from_file()
