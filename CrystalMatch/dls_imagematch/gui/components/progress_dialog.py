from PyQt4.QtGui import QDialog, QIcon, QProgressBar, QVBoxLayout, QLabel


class ProgressDialog(QDialog):

    def __init__(self, caption):
        super(ProgressDialog, self).__init__()

        self._init_ui(caption)

    def _init_ui(self, caption):
        """ Create the basic elements of the user interface.
        """
        self.setFixedWidth(300)
        self.setWindowTitle('Operation Progress')
        self.setWindowIcon(QIcon('web.png'))

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(caption))
        vbox.addWidget(self.progressBar)

        self.setLayout(vbox)

    def on_finished(self):
        self.progressBar.setRange(0, 1)
        self.close()
