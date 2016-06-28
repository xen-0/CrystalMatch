from dls_imagematch.util import  Color
from dls_imagematch.util.config import Config, IntConfigItem, DirectoryConfigItem, ColorConfigItem, BoolConfigItem


class XtalConfig(Config):
    def __init__(self, file):
        Config.__init__(self, file)

        add = self.add

        self.region_size = add(IntConfigItem, "Region Size", default=60, extra_arg='px')
        self.search_width = add(IntConfigItem, "Search Width", default=200, extra_arg='px')
        self.search_height = add(IntConfigItem, "Search Height", default=400, extra_arg='px')
        self.match_translation_only = add(BoolConfigItem, "Translation Only", default=False)
        self.input_dir = add(DirectoryConfigItem, "Input Directory", default="../test-images/")
        self.samples_dir = add(DirectoryConfigItem, "Samples Directory", default="../test-images/Sample Sets/")
        self.output_dir = add(DirectoryConfigItem, "Output Directory", default="../test-output/")
        self.color_align = add(ColorConfigItem, "Align Color", Color.Purple())
        self.color_search = add(ColorConfigItem, "Search Box Color", Color.Orange())
        self.color_xtal_img1 = add(ColorConfigItem, "Img1 Xtal Color", Color.Green())
        self.color_xtal_img2 = add(ColorConfigItem, "Img2 Xtal Color", Color.Red())

        self.initialize_from_file()
