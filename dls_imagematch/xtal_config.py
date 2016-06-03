from dls_imagematch.util import  Color
from dls_imagematch.util.config import Config, IntConfigItem, DirConfigItem, ColorConfigItem


class XtalConfig(Config):
    def __init__(self, file):
        Config.__init__(self, file)

        new = self._new_item

        self.region_size = new(IntConfigItem, "region_size", default=30)
        self.search_width = new(IntConfigItem, "search_width", default=200)
        self.search_height = new(IntConfigItem, "search_height", default=400)
        self.input_dir = new(DirConfigItem, "input_dir_root", default="../test-images/")
        self.samples_dir = new(DirConfigItem, "samples_dir", default="../test-images/Sample Sets/")
        self.output_dir = new(DirConfigItem, "output_dir", default="../test-output/")
        self.color_align = new(ColorConfigItem, "color_align", Color.Purple())
        self.color_search = new(ColorConfigItem, "color_search", Color.Orange())

        self.initialize()