from util.config import ConfigDialog


class XtalConfigDialog(ConfigDialog):
    def __init__(self, config):
        ConfigDialog.__init__(self, config)

        self._init_ui()
        self.finalize_layout()

    def _init_ui(self):
        self.setGeometry(100, 100, 450, 400)

        cfg = self._config
        add = self.add_item

        self.start_group("Colors")
        add(cfg.color_align)
        add(cfg.color_xtal_img1)
        add(cfg.color_xtal_img2)
        add(cfg.color_search)

        self.start_group("Directories")
        add(cfg.input_dir)
        add(cfg.output_dir)
        add(cfg.samples_dir)

        self.start_group("Image Alignment")
        add(cfg.align_detector)
        add(cfg.align_adapt)

        self.start_group("Xtal Search")
        add(cfg.region_size)
        add(cfg.search_width)
        add(cfg.search_height)
        add(cfg.transform_method)
        add(cfg.transform_filter)

        add(cfg.filter_orb)
        add(cfg.filter_surf)
        add(cfg.filter_sift)
        add(cfg.filter_brief)
        add(cfg.filter_brisk)
