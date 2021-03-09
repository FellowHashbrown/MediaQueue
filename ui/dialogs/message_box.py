import sys
from PyQt5 import QtWidgets


class MessageBox(QtWidgets.QDialog):
    """The Message Box is an inheritance from QMessageBox
    for a simplistic Message Box whenever a user forgets to do something
    and the UI must send an error message

    :param title: The title to set for the MessageBox
    :param message: The message to display in the MessageBox
    :param parent: The parent widget for this MessageBox
    """
    def __init__(self, title: str, message: str, parent: QtWidgets.QWidget = None,
                 *, link_url: str = None, link_title: str = None):
        super().__init__(parent)
        self.window().setWindowTitle(title)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        external_link = None
        if link_url is not None:
            external_link = QtWidgets.QLabel(self)
            external_link.setOpenExternalLinks(True)
            if link_title is not None:
                link_title = "<a href={}>{}</a>".format(link_url, link_title)
            else:
                link_title = "<a href={0}>{0}</a>".format(link_url)
            external_link.setText(link_title)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel(message, self))
        if external_link is not None:
            layout.addWidget(external_link)
        layout.addWidget(button_box)
        self.setLayout(layout)

        self.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    m = MessageBox("Test Title", "Test Message")
    m.exec_()
    sys.exit(app.exec_())
