from PyQt4 import QtGui


class ProgressDialog(QtGui.QDialog):

    def __init__(self, caption):
        super(ProgressDialog, self).__init__()

        self._init_ui(caption)

    def _init_ui(self, caption):
        """ Create the basic elements of the user interface.
        """
        self.setFixedWidth(300)
        self.setWindowTitle('Operation Progress')
        self.setWindowIcon(QtGui.QIcon('web.png'))

        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0, 0)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(QtGui.QLabel(caption))
        vbox.addWidget(self.progressBar)

        self.setLayout(vbox)

    def on_finished(self):
        self.progressBar.setRange(0, 1)
        self.close()
