from dls_imagematch.util.config import Config, IntConfigItem, DirectoryConfigItem


class FocusConfig(Config):
    def __init__(self, file):
        Config.__init__(self, file)

        add = self.add

        self.kernel_size = add(IntConfigItem, "Laplacian Kernel Size", default=5, extra_arg='px')
        self.blur_radius = add(IntConfigItem, "Laplacian Blur Radius", default=5, extra_arg='px')
        self.input_dir = add(DirectoryConfigItem, "Input Directory", default="../test-images/focus/ring/")
        self.output_dir = add(DirectoryConfigItem, "Output Directory", default="../test-output/focus/")

        self.initialize_from_file()
