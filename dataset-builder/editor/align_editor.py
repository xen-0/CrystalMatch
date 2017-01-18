from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QListWidget, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QVBoxLayout, \
    QLineEdit, QGroupBox, QPushButton, QMessageBox

from editor.overlay_image_view import OverlayImageView


class AlignmentTestEditor(QMainWindow):
    def __init__(self, test_suite):
        super(AlignmentTestEditor, self).__init__()
        self._test_suite = test_suite
        self._init_ui()

    # noinspection PyUnresolvedReferences
    def _init_ui(self):

        # Set up scaling widget
        self._scale_divider = QLabel(":")
        self._scale_left_value = QLineEdit()
        self._scale_left_value.setMaximumWidth(100)
        self._scale_right_value = QLineEdit()
        self._scale_right_value.setMaximumWidth(100)
        self._scale_value_box = QHBoxLayout()
        self._scale_value_box.addWidget(self._scale_left_value)
        self._scale_value_box.addWidget(self._scale_divider)
        self._scale_value_box.addWidget(self._scale_right_value)

        self._scale_submit = QPushButton("Set scale")
        self._scale_submit.clicked.connect(self._set_scale)
        self._scale_view = QVBoxLayout()
        self._scale_view.addLayout(self._scale_value_box)
        self._scale_view.addWidget(self._scale_submit)
        # TODO: Apply scale changes to overlap image

        self._scale_group_box = QGroupBox()
        self._scale_group_box.setTitle("Scale for data set:")
        self._scale_group_box.setLayout(self._scale_view)
        self._scale_group_box.setFixedWidth(300)

        # Set up test case list
        self._case_list = QListWidget()
        self._case_list.setFixedWidth(300)
        self._case_list.clicked.connect(self._open_test_case)
        self._populate_test_case_list()
        self._instructions = QLabel("Move overlay: w/a/s/d\nShow image 1/2: q/e\n"
                                    "Overlay Images: r\nSave Changes: Enter/Tab")

        left_vbox = QVBoxLayout()
        left_vbox.addWidget(self._scale_group_box)
        left_vbox.addWidget(self._case_list)
        left_vbox.addWidget(self._instructions)

        # Set up viewer
        self._viewer = OverlayImageView("Overlay Viewer")

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_vbox)
        main_layout.addWidget(self._viewer)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        desktop = QDesktopWidget()
        rect = desktop.availableGeometry(desktop.primaryScreen())
        self.setGeometry(rect.width() * 0.15, rect.height() * 0.15, rect.width() * 0.7, rect.height() * 0.7)

        self.show()

    # Button listener methods
    def _set_scale(self):
        try:
            sr1 = float(self._scale_left_value.text())
            sr2 = float(self._scale_right_value.text())
            self._test_suite.set_scale_ratio(sr1, sr2)
            self._test_suite.save_to_file()
        except ValueError:
            QMessageBox().warning(self, "Invalid scale values",
                                  "Scale values must be valid floating points or integer numbers!")

    def _open_test_case(self):
        case = self._get_selected_case()
        self._viewer.overlay_images(case.image_path(1), case.image_path(2))
        x, y = case.get_offset()
        self._viewer.set_overlay_pos(x, y)
        self._current_case_index = self._get_selected_index()

    def keyReleaseEvent(self, *args, **kwargs):
        QMainWindow.keyReleaseEvent(self, *args, **kwargs)
        q_key_press_event = args[0]
        key = q_key_press_event.key()

        # Movement controls
        if key == Qt.Key_W:
            self._viewer.update_overlay_pos(0, -1)
        elif key == Qt.Key_A:
            self._viewer.update_overlay_pos(-1, 0)
        elif key == Qt.Key_S:
            self._viewer.update_overlay_pos(0, 1)
        elif key == Qt.Key_D:
            self._viewer.update_overlay_pos(1, 0)
        # Transparency controls
        elif key == Qt.Key_Q:
            # Show image 1
            self._viewer.set_overlay_opacity(0.1)
        elif key == Qt.Key_E:
            # Show image 2
            self._viewer.set_overlay_opacity(0.9)
        elif key == Qt.Key_R:
            # Overlay images
            self._viewer.set_overlay_opacity(0.5)
        # Other Controls
        elif key == Qt.Key_Return or key == Qt.Key_Tab:
            # Save and move to next record
            x, y = self._viewer.get_overlay_pos()
            case = self._test_suite.cases[self._current_case_index]
            case.set_offset(x, y)
            self._test_suite.save_to_file()
            self._next_case()
            pass

    # Internal methods
    def _next_case(self):
        if self._current_case_index is not None:
            self._current_case_index += 1
            if self._current_case_index > len(self._test_suite.cases):
                self._current_case_index = 0
            self._case_list.setCurrentRow(self._current_case_index)
            self._open_test_case()

    def _get_selected_index(self):
        selected_indexes = self._case_list.selectedIndexes()
        if any(selected_indexes):
            return selected_indexes[0].row()
        return None

    def _get_selected_case(self):
        index = self._get_selected_index()
        if index is not None:
            return self._test_suite.cases[index]
        return None

    def _populate_test_case_list(self):

        # Set scale ratio from the test suite
        sr1, sr2 = self._test_suite.scale_ratio()
        self._scale_left_value.setText(str(sr1))
        self._scale_right_value.setText(str(sr2))

        for test_case in self._test_suite.cases:
            self._case_list.addItem(test_case.name)
