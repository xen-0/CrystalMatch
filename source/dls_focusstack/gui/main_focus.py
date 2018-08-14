from __future__ import division

import sys
from os import listdir, makedirs
from os.path import isfile, join, exists, isdir

from PyQt4 import QtGui
from PyQt4.QtGui import (QWidget, QMainWindow, QIcon, QHBoxLayout, QVBoxLayout, QAction)

from config.focus_config import FocusConfig
from dls_focusstack.focus.focus_stack_lap_pyramid import FocusStack
from dls_focusstack.gui import *

sys.path.append("..")


class FocusStackerMain(QMainWindow):
    def __init__(self, config_dir, output_dir, default_input_dir=""):
        super(FocusStackerMain, self).__init__()

        self._config_dir = config_dir

        self.init_ui()
        self._output_dir = output_dir
        if not (exists(output_dir) and isdir(output_dir)):
            makedirs(output_dir)
        self.open_folder(default_input_dir)

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Focus Stacking')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        self._image_list = ImageList()
        self._frame = ImageFrame()

        self._image_list.signal_selected.connect(self._frame.display_image)

        btn_go = QtGui.QPushButton("Start")
        btn_go.setFixedHeight(50)
        btn_go.setStyleSheet("font-size: 20pt;")
        btn_go.clicked.connect(self.do_stacking)

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(btn_go)
        vbox_left.addWidget(self._image_list)

        hbox_main = QHBoxLayout()
        hbox_main.setSpacing(10)
        hbox_main.addLayout(vbox_left)
        hbox_main.addWidget(self._frame)
        hbox_main.addStretch(1)

        main_widget = QWidget()
        main_widget.setLayout(hbox_main)
        self.setCentralWidget(main_widget)
        self.show()

    def init_menu_bar(self):
        """Create and populate the menu bar. """
        # Exit Application
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        load_action = QAction(QIcon('exit.png'), '&Load', self)
        load_action.setShortcut('Ctrl+O')
        load_action.setStatusTip('Load Images')
        load_action.triggered.connect(self._fn_load_images)

        # Open options dialog
        options_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Options', self)
        options_action.setShortcut('Ctrl+O')
        options_action.setStatusTip('Open Options Dialog')
        options_action.triggered.connect(self._fn_config_dialog)

        # Create menu bar
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(load_action)
        file_menu.addAction(exit_action)

        option_menu = menu_bar.addMenu('&Option')
        option_menu.addAction(options_action)

    def _fn_load_images(self):
        # Choose target folder
        folder_path = str(QtGui.QFileDialog.getExistingDirectory(self, 'Choose directory'))
        self.open_folder(folder_path)

    def _fn_config_dialog(self):
        dialog = FocusConfigDialog(FocusConfig(join(self._config_dir, FocusStack.CONFIG_FILE_NAME)))
        dialog.exec_()

    def open_folder(self, folder_path):
        # Get list of all files in folder
        files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

        # Filter for image files
        included_extensions = ['jpg', 'bmp', 'png', 'gif', 'jpeg', 'tif']
        image_files = [fn for fn in files if any(fn.lower().endswith(ext) for ext in included_extensions)]

        folder_path += "/"
        #"\\" - TODO better way of doing this
        files = [folder_path + f for f in image_files]

        self._image_list.set_images(files)

    def do_stacking(self):
        images = self._image_list.get_checked_images()

        if len(images) > 1:
            stacker = FocusStack(images, self._config_dir)
            merged = stacker.composite()

            print("Complete")

            self._frame.display_image(merged)
            merged.save(join(self._output_dir, "merged.png"))
            # merged.popup()
