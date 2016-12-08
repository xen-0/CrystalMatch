from PyQt4.QtGui import QMainWindow, QListWidget, QHBoxLayout, QWidget


class AlignmentTestEditor(QMainWindow):
    def __init__(self, test_suite):
        super(AlignmentTestEditor, self).__init__()
        self._test_suite = test_suite
        self._init_ui()

    # noinspection PyUnresolvedReferences
    def _init_ui(self):
        # Set up test case list
        self._case_list = QListWidget()
        # self._case_list.setFixedSize(200, 350)
        self._case_list.clicked.connect(self._open_test_case)
        self._populate_test_case_list()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self._case_list)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.show()

    # Button listener methods
    def _open_test_case(self):
        # TODO: display test case
        pass

    # Internal methods
    def _populate_test_case_list(self):
        for test_case in self._test_suite.cases:
            self._case_list.addItem(test_case.name)
