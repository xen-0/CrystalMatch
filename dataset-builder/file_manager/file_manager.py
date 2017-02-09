from os import makedirs, listdir
from os.path import exists, isdir, join, basename
from string import strip

from PyQt4.QtGui import QMainWindow, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSpacerItem, \
    QMessageBox, QLineEdit, QLabel, QGroupBox, QRadioButton

from editor.align_editor import AlignmentTestEditor
from editor.poi_editor import PoiTestEditor
from file_selector import DirSelector
from test_suite import CrystalTestSuite


class FileManager(QMainWindow):
    """ GUI utility which allows the selection and creation of dataset files. """

    def __init__(self, data_sets_dir, img_dir_root):
        super(FileManager, self).__init__()
        self._active_windows = []

        # Store root paths and ensure they exist
        self._img_dir_root = img_dir_root
        self._touch_dir_path(img_dir_root)
        self._data_sets_dir = data_sets_dir
        self._touch_dir_path(data_sets_dir)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Crystal Match Data-set Builder')

        self._init_ui()
        self.show()

    # noinspection PyUnresolvedReferences
    def _init_ui(self):
        # Create Open with option box
        self._group_open_with = QGroupBox("Open with:")
        self._radio_align_editor = QRadioButton("Alignment editor")
        self._radio_poi_editor = QRadioButton("POI editor")
        vbox_group = QVBoxLayout()
        vbox_group.addWidget(self._radio_align_editor)
        vbox_group.addWidget(self._radio_poi_editor)
        self._group_open_with.setLayout(vbox_group)
        self._radio_align_editor.setChecked(True)

        # Create file selection list boxes
        self._label_data_sets = QLabel("Data Sets:")

        self._list_datasets = QListWidget()
        self._list_datasets.doubleClicked.connect(self._open_editor)
        self._load_datasets()

        vbox_datasets = QVBoxLayout()
        vbox_datasets.addWidget(self._group_open_with)
        vbox_datasets.addWidget(self._label_data_sets)
        vbox_datasets.addWidget(self._list_datasets)

        # Create the new file section
        self._file_select_1 = DirSelector("Formulatrix Image Dir", 100)
        self._file_select_2 = DirSelector("Beamline Image Dir", 100)

        self._label_new_file_name = QLabel("New File Name:")
        self._text_new_file_name = QLineEdit()

        self._button_new_dataset = QPushButton("Create Data Set")
        self._button_new_dataset.clicked.connect(self._new_data_set)

        vbox_new_file = QVBoxLayout()
        vbox_new_file.addWidget(self._file_select_1)
        vbox_new_file.addWidget(self._file_select_2)
        vbox_new_file.addWidget(self._label_new_file_name)
        vbox_new_file.addWidget(self._text_new_file_name)
        vbox_new_file.addWidget(self._button_new_dataset)
        vbox_new_file.addSpacerItem(QSpacerItem(100, 100))

        # Set the main window layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(vbox_datasets)
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
        self._list_datasets.clear()
        for path in listdir(self._data_sets_dir):
            self._list_datasets.addItem(path)

    def _open_editor(self):
        data_set_file = self._list_datasets.selectedItems()[0]
        data_set_file_path = join(self._data_sets_dir, str(data_set_file.text()))

        if self._radio_align_editor.isChecked():
            self._open_alignment_editor(data_set_file_path)
        elif self._radio_poi_editor.isChecked():
            self._open_poi_editor(data_set_file_path)
        else:
            raise Exception("Editor type not set")

    def _new_data_set(self):
        new_file_path = self._generate_new_file_path(self._data_sets_dir)
        dir_1 = self._file_select_1.get_dir()
        dir_2 = self._file_select_2.get_dir()
        # Validate directories
        if self._is_valid_dir(dir_1) and self._is_valid_dir(dir_2) and self._is_valid_new_file_path(new_file_path):
            new_test_suite = CrystalTestSuite(new_file_path, self._img_dir_root)
            new_test_suite.create_cases_from_files(dir_1, dir_2)
            new_test_suite.save_to_file()

            # Reload the data set lists
            self._load_datasets()

    # Internal Logic
    def _open_poi_editor(self, poi_data_set_path):
        test_suite = CrystalTestSuite(poi_data_set_path, self._img_dir_root)
        self._active_windows.append(PoiTestEditor(test_suite))

    def _open_alignment_editor(self, file_path):
        test_suite = CrystalTestSuite(file_path, self._img_dir_root)
        self._active_windows.append(AlignmentTestEditor(test_suite))

    def _is_valid_new_file_path(self, new_file_path):
        if basename(new_file_path) == ".json":
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
        if not new_file_name.endswith(".json"):
            new_file_name += ".json"
        new_file_path = join(parent_dir, new_file_name)
        return new_file_path

    def _is_valid_dir(self, dir_path):
        passed = exists(dir_path) and isdir(dir_path)
        if not passed:
            QMessageBox().warning(self, "Invalid Directory",
                                  "Please select directories before creating a new data set.")
        return passed
