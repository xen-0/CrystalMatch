import sys

from PyQt4 import QtGui

from file_manager.file_manager import FileManager


def main():
    data_sets_dir = "../test-images/data-sets/"
    img_dir_root = "../test-images/"

    app = QtGui.QApplication(sys.argv)

    # noinspection PyUnusedLocal
    manager = FileManager(data_sets_dir, img_dir_root)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
