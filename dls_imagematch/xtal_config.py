from dls_imagematch.util import  Color
from dls_imagematch.util.config import Config, IntConfigItem, DirectoryConfigItem, ColorConfigItem


class XtalConfig(Config):
    def __init__(self, file):
        Config.__init__(self, file)

        new = self._new_item

        self.region_size = new(IntConfigItem, "Region Size", default=30, arg1='px')
        self.search_width = new(IntConfigItem, "Search Width", default=200, arg1='px')
        self.search_height = new(IntConfigItem, "Search Height", default=400, arg1='px')
        self.input_dir = new(DirectoryConfigItem, "Input Directory", default="../test-images/")
        self.samples_dir = new(DirectoryConfigItem, "Samples Directory", default="../test-images/Sample Sets/")
        self.output_dir = new(DirectoryConfigItem, "Output Directory", default="../test-output/")
        self.color_align = new(ColorConfigItem, "Align Color", Color.Purple())
        self.color_search = new(ColorConfigItem, "Search Box Color", Color.Orange())
        self.color_xtal_img1 = new(ColorConfigItem, "Img1 Xtal Color", Color.Green())
        self.color_xtal_img2 = new(ColorConfigItem, "Img2 Xtal Color", Color.Red())

        self.initialize()
