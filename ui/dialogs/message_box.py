import sys
from PyQt5 import QtWidgets


class MessageBox(QtWidgets.QMessageBox):
    """The Message Box is an inheritance from QMessageBox
    for a simplistic Message Box whenever a user forgets to do something
    and the UI must send an error message

    :param title: The title to set for the MessageBox
    :param message: The message to display in the MessageBox
    :param parent: The parent widget for this MessageBox
    """
    def __init__(self, title: str, message: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setText(message)
        self.setWindowTitle(title)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    m = MessageBox("Test Title", "Test Message")
    m.exec_()
    sys.exit(app.exec_())
