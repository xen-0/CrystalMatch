from PyQt4.QtGui import QComboBox, QGroupBox, QTextEdit, QLineEdit, QHBoxLayout, QPushButton, QDialog, QFileDialog


class DirSelector(QGroupBox):
    """A custom widget which allows use"""

    def __init__(self, title, height):
        QGroupBox.__init__(self)
        self.setTitle(title)
        self.setFixedHeight(height)
        self._init_ui()

    def get_dir(self):
        return str(self._text_directory.text())

    # noinspection PyUnresolvedReferences
    def _init_ui(self):
        self._text_directory = QLineEdit()
        self._button_browse = QPushButton("...")
        self._button_browse.clicked.connect(self._select_dir)

        hbox = QHBoxLayout()
        hbox.addWidget(self._text_directory)
        hbox.addWidget(self._button_browse)

        self.setLayout(hbox)

    def _select_dir(self):
        self._text_directory.setText(QFileDialog().getExistingDirectory())
