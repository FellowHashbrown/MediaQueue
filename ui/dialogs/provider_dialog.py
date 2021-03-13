from PyQt5 import QtWidgets, QtCore

from ui import MessageBox, ProviderListScrollArea
from options import options


class ProviderDialog(QtWidgets.QDialog):
    """The Provider Dialog allows a user to specify the Streaming Providers
    they want in the Media Queue.

    There are 2 default ones including Unavailable and Default which cannot be removed.
    """

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, update_func: callable = None):
        super().__init__(parent)
        self.update_func = update_func

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignHCenter)

        self.setWindowTitle("Configure Streaming Providers")
        self.scroll_area = ProviderListScrollArea(self, remove_provider_func=self.remove_provider)
        self.add_button = QtWidgets.QPushButton("Add Streaming Provider", self)
        self.add_button.clicked.connect(self.ask_for_provider)
        self.add_button.setToolTip("Add a new provider to the provider list")

        layout.addWidget(self.scroll_area)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def ask_for_provider(self):
        """Asks the user for a new Streaming Provider to add to the Streaming Provider list"""
        provider, accepted = QtWidgets.QInputDialog.getText(
            self, "New Streaming Provider",
            "Enter the Streaming Provider: ")
        if accepted:
            if options.add_provider(provider):
                self.update_func()
                self.scroll_area.update_ui()
            else:
                MessageBox("Streaming Provider Exists!",
                           f"\"{provider}\" already exists in the app.")

    def remove_provider(self, index: int):
        """Removes a Streaming Provider from the provider list

        :param index: The index of the Streaming Provider to remove
        """
        if options.remove_provider(index):
            self.update_func()
            self.scroll_area.update_ui()
        else:
            MessageBox("Can't Remove That!",
                       (
                           "If you tried removing Default or Unavailable, you can't do that.\n" +
                           "If you were trying to remove something else, then this is a bug and you should report it!\n"+
                           "Check under the Help menu for that!"
                       ))
