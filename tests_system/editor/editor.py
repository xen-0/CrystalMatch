from os.path import dirname
from sys import path
path.append(dirname(path[0]))

from PyQt4 import QtGui
from PyQt4.QtGui import QMainWindow, QIcon, QAction, QListWidget, QHBoxLayout, QWidget, QVBoxLayout, QPushButton

from dls_util.imaging import Color
from dls_imagematch.gui.components import ImageSelector
from dls_imagematch.gui.crystal import PointSelectDialog


class TestEditor(QMainWindow):
    """ Small GUI utility to allow configuration options for the Crystal image matching application to be set.
    """
    def __init__(self, test_suite):
        super(TestEditor, self).__init__()

        self._test_suite = test_suite
        self._cases = self._test_suite.cases

        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle('Crystal Match Test Case Editor')

        self.init_menu_bar()

        self._init_ui()
        self._new_selection()

        self.show()

    def init_menu_bar(self):
        """Create and populate the menu bar. """
        # Exit Application
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        save_action = QAction(QIcon('exit.png'), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save All')
        save_action.triggered.connect(self._save_all)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)
        file_menu.addAction(save_action)

    def _init_ui(self):
        # --- Test Case List widget ---
        self._case_list = QListWidget()
        self._case_list.setFixedSize(300, 700)
        self._case_list.clicked.connect(self._new_selection)

        for case in self._cases:
            self._case_list.addItem(case.name)

        # --- Image frames ---
        self._frame_1, vbox_frame_1 = self._ui_make_image_frame(1)
        self._frame_2, vbox_frame_2 = self._ui_make_image_frame(2)

        # --- Layout ---
        hbox_frame = QHBoxLayout()
        hbox_frame.addLayout(vbox_frame_1)
        hbox_frame.addLayout(vbox_frame_2)
        hbox_frame.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addWidget(self._case_list)
        hbox.addLayout(hbox_frame)
        hbox.addStretch(1)

        vbox_main = QVBoxLayout()
        vbox_main.setSpacing(10)
        vbox_main.addLayout(hbox)
        vbox_main.addStretch(1)

        main_widget = QWidget()
        main_widget.setLayout(vbox_main)
        self.setCentralWidget(main_widget)
        self.show()

    def _ui_make_image_frame(self, img_num):
        ImageSelector.IMAGE_SIZE = 600
        frame = ImageSelector("Image {}".format(img_num), None)
        frame.set_button_visible(False)

        btn_points = QPushButton("Select Points")
        btn_points.clicked.connect(lambda: self._select_points_clicked(img_num))

        hbox = QHBoxLayout()
        hbox.addWidget(btn_points)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(frame)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        return frame, vbox

    def _get_selected_index(self):
        selected = self._case_list.selectedIndexes()
        if any(selected):
            return selected[0].row()
        else:
            return -1

    def _get_selected_case(self):
        index = self._get_selected_index()
        if index != -1:
            return self._cases[index]
        else:
            return None

    def _new_selection(self):
        """ Called when a new case is selected in the list; displays the case's image 1 with points marked. """
        case = self._get_selected_case()
        if case is not None:
            self._frame_1.set_image(case.image_marked(1))
            self._frame_2.set_image(case.image_marked(2))

    def _select_points_clicked(self, img_num):
        """ Called when the select points button is pushed. Displays a dialog that allows the user to
        select points on the first image. """
        case = self._get_selected_case()
        if case is None:
            return

        image = case.image(img_num)

        ok, points = self._get_points_from_user_selection(image)
        if ok:
            case.set_image_points(points, img_num)
            self._new_selection()

    def _get_points_from_user_selection(self, image):
        """ Display a dialog and return the result to the caller. """
        max_points = 10
        size = 100
        color = Color.green()
        dialog = PointSelectDialog(self, image, max_points, size, color)
        result_ok = dialog.exec_()

        points = []
        if result_ok:
            points = dialog.selected_points()
            points = [p.intify() for p in points]

        return result_ok, points

    def _save_all(self):
        self._test_suite.save_to_file()


