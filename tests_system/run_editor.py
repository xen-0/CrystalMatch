import sys

from PyQt4 import QtGui
from editor.editor import TestEditor
from test_suite import CrystalTestSuite


def main():
    config_dir = "../config/"
    case_file = "./data/cases_blank.csv"
    img_dir = "../test-images/Formulatrix/"

    suite = CrystalTestSuite(case_file, img_dir)

    app = QtGui.QApplication(sys.argv)
    ex = TestEditor(suite)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
