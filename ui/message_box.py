from PyQt5 import QtWidgets


class MessageBox(QtWidgets.QMessageBox):
    def __init__(self, title: str, message: str, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setText(message)
        self.setWindowTitle(title)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.exec()
