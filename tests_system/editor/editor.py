from os.path import dirname
from sys import path

from PyQt4.QtCore import Qt

from magnifying_image_view import MagnifyingImageView

path.append(dirname(path[0]))

from PyQt4 import QtGui
from PyQt4.QtGui import QMainWindow, QIcon, QAction, QListWidget, QHBoxLayout, QWidget, QVBoxLayout, QKeySequence

from dls_imagematch.gui.components import ImageSelector


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
        self._case_list.setFixedSize(300, 350)
        self._case_list.clicked.connect(self._new_selection)

        self._point_list = QListWidget()
        self._point_list.setFixedSize(300, 350)
        self._point_list.clicked.connect(self._select_point)

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(self._case_list)
        vbox_left.addWidget(self._point_list)

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
        hbox.addLayout(vbox_left)
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
        frame = MagnifyingImageView("Image {}".format(img_num))

        vbox = QVBoxLayout()
        vbox.addWidget(frame)
        vbox.addStretch(1)

        return frame, vbox

    def _select_point(self):
        point_set = self._get_selected_point()
        if point_set is not None:
            self._frame_1.select_point(point_set[0])
            self._frame_2.select_point(point_set[1])

    def _get_selected_point(self):
        index = self._get_selected_index(self._point_list)
        if index != -1:
            return self._point_list_data[index]
        return None

    @staticmethod
    def _get_selected_index(list_widget):
        selected = list_widget.selectedIndexes()
        if any(selected):
            return selected[0].row()
        else:
            return -1

    def _get_selected_case(self):
        index = self._get_selected_index(self._case_list)
        if index != -1:
            return self._cases[index]
        else:
            return None

    def _new_selection(self):
        """ Called when a new case is selected in the list; displays the case's image 1 with points marked. """
        case = self._get_selected_case()
        if case is not None:
            self._frame_1.set_image(case.image_path(1))
            self._frame_2.set_image(case.image_path(2))
            self._load_points_for_selected_case()

    def _load_points_for_selected_case(self):
        self._point_list.clear()
        case = self._get_selected_case()
        points_1 = case.image_points(1)
        points_2 = case.image_points(2)
        self._point_list_data = []
        # Build the data model from case data
        for i in range(max(len(points_1), len(points_2))):
            pt_1, pt_2 = None, None
            if i < len(points_1):
                pt_1 = points_1[i]
            if i < len(points_2):
                pt_2 = points_2[i]
            self._point_list_data.append((pt_1, pt_2))
        # Print the results to the list
        for p in self._point_list_data:
            str_1 = str(p[0]) if p[0] is not None else "?"
            str_2 = str(p[1]) if p[1] is not None else "?"
            self._point_list.addItem(str_1 + " -> " + str_2)

        # Write points to the displayed images
        self._frame_1.update_points_data(points_1)
        self._frame_2.update_points_data(points_2)

    def _save_all(self):
        self._test_suite.save_to_file()
