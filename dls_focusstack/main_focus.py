from __future__ import division

import sys
from os import listdir
from os.path import isfile, join

from PyQt4 import QtGui
from PyQt4.QtGui import (QWidget, QMainWindow, QIcon, QHBoxLayout, QApplication, QAction)

from dls_focusstack.gui import ImageList, ImageFrame
from dls_focusstack.focus import focus_stack

sys.path.append("..")


class FocusStacker(QMainWindow):

    def __init__(self):
        super(FocusStacker, self).__init__()

        self.init_ui()

        self.open_folder("../focusstack/Input/ring")

    def init_ui(self):
        """ Create all elements of the user interface. """
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowTitle('Diamond VMXi Focus Stacking')
        self.setWindowIcon(QIcon('web.png'))

        self.init_menu_bar()

        self._image_list = ImageList()
        self._frame = ImageFrame()

        self._image_list.signal_selected.connect(self._frame.display_image)

        btn_go = QtGui.QPushButton("Go")
        btn_go.clicked.connect(self.do_stacking)


        hbox_main = QHBoxLayout()
        hbox_main.setSpacing(10)
        hbox_main.addWidget(self._image_list)
        hbox_main.addWidget(btn_go)
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

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(load_action)
        file_menu.addAction(exit_action)

    def _fn_load_images(self):
        # Choose target folder
        folder_path = str(QtGui.QFileDialog.getExistingDirectory(self, 'Choose directory'))
        self.open_folder(folder_path)

    def open_folder(self, folder_path):
        # Get list of all files in folder
        files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

        # Filter for image files
        included_extensions = ['jpg', 'bmp', 'png', 'gif', 'jpeg']
        image_files = [fn for fn in files if any(fn.lower().endswith(ext) for ext in included_extensions)]

        folder_path += "\\"
        files = [folder_path + f for f in image_files]

        self._image_list.set_images(files)

    def do_stacking(self):
        images = self._image_list.get_checked_images()

        if len(images) > 1:
            merged = focus_stack(images)
            self._frame.display_image(merged)
            merged.save("../test-output/merged.png")





def main():
    app = QApplication(sys.argv)
    ex = FocusStacker()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
