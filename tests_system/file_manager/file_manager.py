from PyQt4.QtGui import QMainWindow, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from os.path import exists, isdir, join

from os import makedirs, listdir

from editor.editor import TestEditor
from test_suite import CrystalTestSuite


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

        self.setGeometry(400, 400, 600, 600)
        self.setWindowTitle('Crystal Match Data-set Builder')

        self._init_ui()
        self.show()

    # noinspection PyUnresolvedReferences
    def _init_ui(self):

        self._label_poi_data_sets = QLabel("POI Data Sets:")
        self._label_align_data_sets = QLabel("Alignment Data Sets:")

        self._list_poi_datasets = QListWidget()
        self._list_poi_datasets.doubleClicked.connect(self._open_poi_data_set)
        self._list_align_datasets = QListWidget()
        self._load_datasets()

        self._button_new_poi_test = QPushButton()
        self._button_new_poi_test = QPushButton("New POI Test")

        self._button_new_align_test = QPushButton()
        self._button_new_align_test = QPushButton("New Alignment Test")

        vbox_poi = QVBoxLayout()
        vbox_poi.addWidget(self._label_poi_data_sets)
        vbox_poi.addWidget(self._list_poi_datasets)
        vbox_poi.addWidget(self._button_new_poi_test)

        vbox_align = QVBoxLayout()
        vbox_align.addWidget(self._label_align_data_sets)
        vbox_align.addWidget(self._list_align_datasets)
        vbox_align.addWidget(self._button_new_align_test)

        main_layout = QHBoxLayout()
        main_layout.addLayout(vbox_poi)
        main_layout.addLayout(vbox_align)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.show()

    def _load_datasets(self):
        for path in listdir(self._poi_test_dir):
            self._list_poi_datasets.addItem(path)
        for path in listdir(self._align_test_dir):
            self._list_align_datasets.addItem(path)

    def _open_poi_data_set(self):
        poi_data_set_file = self._list_poi_datasets.selectedItems()[0]
        poi_data_set_path = join(self._poi_test_dir, str(poi_data_set_file.text()))
        test_suite = CrystalTestSuite(poi_data_set_path, self._img_dir_root)
        self._active_windows.append(TestEditor(test_suite))

    @staticmethod
    def _touch_dir_path(directory):
        if not exists(directory) or not isdir(directory):
            makedirs(directory)
