from util.config.config_dialog import ConfigDialog


class FocusConfigDialog(ConfigDialog):
    def __init__(self, config):
        ConfigDialog.__init__(self, config)

        self._init_ui()
        self.finalize_layout()

    def _init_ui(self):
        self.setGeometry(100, 100, 450, 400)

        cfg = self._config
        add = self.add_item

        self.start_group("Image Alignment")
        add(cfg.align_method)
        add(cfg.align_adapt)

        self.start_group("Focus Stacking")
        add(cfg.kernel_size)
        add(cfg.blur_radius)

        self.start_group("Directories")
        add(cfg.input_dir)
        add(cfg.output_dir)
