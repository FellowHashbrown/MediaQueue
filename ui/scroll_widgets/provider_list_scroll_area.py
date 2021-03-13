from functools import partial
from PyQt5 import QtWidgets, QtCore

from ui import add_grid_to_layout
from options import options


class ProviderListScrollArea(QtWidgets.QScrollArea):
    """The Provider List Scroll Area is the scroll area
    meant to display all the names of the Streaming Providers that a user
    sets for the Provider attribute of a piece of Media

    """

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, remove_provider_func: callable = None):
        super().__init__(parent)

        # Save the parameters as attributes
        self.remove_provider_func = remove_provider_func

        # Create the widget attributes for inside the scroll area
        self.widget = None
        self.widgets = None

        self.update_ui()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_ui(self):
        """Creates/Updates the UI for the list of providers"""

        # Setup the widgets and labels for the Scroll Area
        self.widget = QtWidgets.QWidget(self.parent())
        layout = QtWidgets.QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.widgets = []
        providers = options.get_providers()
        for i in range(len(providers)):
            provider = providers[i]

            provider_label = QtWidgets.QLabel(provider, self.widget)

            remove_button = QtWidgets.QPushButton("Remove", self.widget)
            remove_button.clicked.connect(partial(self.remove_provider_func, i))
            remove_button.setToolTip(f"Remove {provider} from the provider list")

            self.widgets.append([provider_label, remove_button])
        add_grid_to_layout(self.widgets, layout)
        self.widget.setLayout(layout)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
