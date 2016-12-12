from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QListWidget, QHBoxLayout, QWidget, QDesktopWidget, QLabel, QVBoxLayout

from editor.overlay_image_view import OverlayImageView


class AlignmentTestEditor(QMainWindow):
    def __init__(self, test_suite):
        super(AlignmentTestEditor, self).__init__()
        self._test_suite = test_suite
        self._init_ui()

    # noinspection PyUnresolvedReferences
    def _init_ui(self):
        # Set up test case list
        self._case_list = QListWidget()
        self._case_list.setFixedWidth(300)
        self._case_list.clicked.connect(self._open_test_case)
        self._populate_test_case_list()
        self._instructions = QLabel("Move overlay: w/a/s/d\nShow image 1/2: q/e\n"
                                    "Overlay Images: r\nSave Changes: Enter/Tab")

        left_vbox = QVBoxLayout()
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
    def _open_test_case(self):
        case = self._get_selected_case()
        self._viewer.overlay_images(case.image_path(1), case.image_path(2))
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
            # TODO: Save to file
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
        for test_case in self._test_suite.cases:
            self._case_list.addItem(test_case.name)
