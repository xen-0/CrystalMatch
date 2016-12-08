from os import makedirs, listdir
from os.path import exists, isdir, join, basename
from string import strip

from PyQt4.QtGui import QMainWindow, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSpacerItem, \
    QMessageBox, QLineEdit, QLabel
from enum import Enum

from editor.editor import TestEditor
from file_selector import DirSelector
from test_suite import CrystalTestSuite


class EnumTestSuiteType(Enum):
    poi_case = 1
    alignment_case = 2


class FileManager(QMainWindow):
    """ GUI utility which allows the selection and creation of dataset files. """

    DIR_ALIGNMENT_TESTS = "alignment"
    DIR_POI_TESTS = "poi_matching"

    def __init__(self, data_sets_dir, img_dir_root):
        super(FileManager, self).__init__()
        self._active_windows = []

        # Store root paths and ensure they exist
        self._img_dir_root = img_dir_root
        self._touch_dir_path(img_dir_root)
        self._data_sets_dir = data_sets_dir
        self._poi_test_dir = join(data_sets_dir, self.DIR_POI_TESTS)
        self._align_test_dir = join(data_sets_dir, self.DIR_ALIGNMENT_TESTS)
        self._touch_dir_path(self._poi_test_dir)
        self._touch_dir_path(self._align_test_dir)

        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle('Crystal Match Data-set Builder')

        self._init_ui()
        self.show()

    # noinspection PyUnresolvedReferences
    def _init_ui(self):
        # Create file selection list boxes
        self._label_poi_data_sets = QLabel("POI Data Sets:")
        self._label_align_data_sets = QLabel("Alignment Data Sets:")

        self._list_poi_datasets = QListWidget()
        self._list_poi_datasets.doubleClicked.connect(self._open_poi_data_set)
        self._list_align_datasets = QListWidget()
        self._list_align_datasets.doubleClicked.connect(self._open_alignment_editor)
        self._load_datasets()

        vbox_poi = QVBoxLayout()
        vbox_poi.addWidget(self._label_poi_data_sets)
        vbox_poi.addWidget(self._list_poi_datasets)

        vbox_align = QVBoxLayout()
        vbox_align.addWidget(self._label_align_data_sets)
        vbox_align.addWidget(self._list_align_datasets)

        # Create the new file section
        self._file_select_1 = DirSelector("Directory 1", 100)
        self._file_select_2 = DirSelector("Directory 2", 100)

        self._label_new_file_name = QLabel("New File Name:")
        self._text_new_file_name = QLineEdit()

        self._button_new_poi_test = QPushButton("New POI Test")
        self._button_new_poi_test.clicked.connect(self._new_poi_data_set)

        self._button_new_align_test = QPushButton("New Alignment Test")
        self._button_new_align_test.clicked.connect(self._new_alignment_data_set)

        vbox_new_file = QVBoxLayout()
        vbox_new_file.addWidget(self._file_select_1)
        vbox_new_file.addWidget(self._file_select_2)
        vbox_new_file.addWidget(self._label_new_file_name)
        vbox_new_file.addWidget(self._text_new_file_name)
        vbox_new_file.addWidget(self._button_new_poi_test)
        vbox_new_file.addWidget(self._button_new_align_test)
        vbox_new_file.addSpacerItem(QSpacerItem(100, 100))

        # Set the main window layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(vbox_poi)
        main_layout.addLayout(vbox_align)
        main_layout.addLayout(vbox_new_file)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.show()

    @staticmethod
    def _touch_dir_path(directory):
        if not exists(directory) or not isdir(directory):
            makedirs(directory)

    # Button listener methods
    def _load_datasets(self):
        self._list_poi_datasets.clear()
        self._list_align_datasets.clear()
        for path in listdir(self._poi_test_dir):
            self._list_poi_datasets.addItem(path)
        for path in listdir(self._align_test_dir):
            self._list_align_datasets.addItem(path)

    def _open_poi_data_set(self):
        poi_data_set_file = self._list_poi_datasets.selectedItems()[0]
        poi_data_set_path = join(self._poi_test_dir, str(poi_data_set_file.text()))
        self._open_poi_editor(poi_data_set_path)

    def _open_alignment_data_set(self):
        align_data_set_file = self._list_align_datasets.selectedItems()[0]
        align_data_set_file = join(self._align_test_dir, str(align_data_set_file.text()))
        self._open_alignment_editor(align_data_set_file)

    def _new_poi_data_set(self):
        self._create_new_data_set(EnumTestSuiteType.poi_case)

    def _new_alignment_data_set(self):
        self._create_new_data_set(EnumTestSuiteType.alignment_case)

    # Internal Logic
    def _open_poi_editor(self, poi_data_set_path):
        test_suite = CrystalTestSuite(poi_data_set_path, self._img_dir_root)
        self._active_windows.append(TestEditor(test_suite))

    def _open_alignment_editor(self, file_path):
        # TODO: Add code to launch alignment editor
        print "Alignment Editor under construction..."
        # test_suite = CrystalTestSuite(file_path, self._img_dir_root)
        # self._active_windows.append(TestEditor(test_suite))

    def _create_new_data_set(self, test_type):
        if test_type is EnumTestSuiteType.poi_case:
            parent_dir = self._poi_test_dir
        elif test_type is EnumTestSuiteType.alignment_case:
            parent_dir = self._align_test_dir
        else:
            raise ValueError("test_type not recognised - expected EnumTestSuiteType value.")
        new_file_path = self._generate_new_file_path(parent_dir)
        dir_1 = self._file_select_1.get_dir()
        dir_2 = self._file_select_2.get_dir()
        # Validate directories
        if self._is_valid_dir(dir_1) and self._is_valid_dir(dir_2) and self._is_valid_new_file_path(new_file_path):
            new_test_suite = CrystalTestSuite(new_file_path, self._img_dir_root)
            new_test_suite.create_cases_from_files(dir_1, dir_2)
            new_test_suite.save_to_file()

            # Reload the data set lists and open the editor
            self._load_datasets()
            if test_type is EnumTestSuiteType.poi_case:
                self._open_poi_editor(new_file_path)
            elif test_type is EnumTestSuiteType.alignment_case:
                self._open_alignment_editor(new_file_path)

    def _is_valid_new_file_path(self, new_file_path):
        if basename(new_file_path) == ".csv":
            QMessageBox().warning(self, "Invalid Filename",
                                  "Please enter a file name!")
            return False
        if exists(new_file_path):
            QMessageBox().warning(self, "Invalid Filename",
                                  "A data set with that name already exists! Please choose a different file name.")
            return False
        return True

    def _generate_new_file_path(self, parent_dir):
        new_file_name = strip(str(self._text_new_file_name.text()))
        if not new_file_name.endswith(".csv"):
            new_file_name += ".csv"
        new_file_path = join(parent_dir, new_file_name)
        return new_file_path

    def _is_valid_dir(self, dir_path):
        passed = exists(dir_path) and isdir(dir_path)
        if not passed:
            QMessageBox().warning(self, "Invalid Directory",
                                  "Please select directories before creating a new data set.")
        return passed
