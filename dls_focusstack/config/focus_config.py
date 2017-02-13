from dls_util.config import Config, IntConfigItem, DirectoryConfigItem


class FocusConfig(Config):
    def __init__(self, filename):
        Config.__init__(self, filename)

        add = self.add

        self.kernel_size = add(IntConfigItem, "Laplacian Kernel Size", default=5, extra_arg='px')
        self.blur_radius = add(IntConfigItem, "Laplacian Blur Radius", default=5, extra_arg='px')

        self.initialize_from_file()
