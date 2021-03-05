import sys

from PyQt5.QtWidgets import QApplication

from ui import MediaQueue

if __name__ == "__main__":
    app = MediaQueue(sys.argv)
    res = app.exec_()

    sys.exit(res)
