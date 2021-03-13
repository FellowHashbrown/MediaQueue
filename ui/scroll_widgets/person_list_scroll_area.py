from functools import partial
from PyQt5 import QtWidgets, QtCore

from ui import add_grid_to_layout
from options import options


class PersonListScrollArea(QtWidgets.QScrollArea):
    """The Person List Scroll Area is the scroll area
    meant to display all the names of the People that a yser
    sets for the Person attribute of a piece of Media

    """

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, remove_person_func: callable = None):
        super().__init__(parent)

        # Save the parameters as attributes
        self.remove_person_func = remove_person_func

        # Create the widget attributes for inside the scroll area
        self.widget = None
        self.widgets = None

        self.update_ui()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_ui(self):
        """Creates/Updates the UI for the list of people"""

        # Setup the widgets and labels for the Scroll Area
        self.widget = QtWidgets.QWidget(self.parent())
        layout = QtWidgets.QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.widgets = []
        persons = options.get_persons()
        for i in range(len(persons)):
            person = persons[i]

            person_label = QtWidgets.QLabel(person, self.widget)

            remove_button = QtWidgets.QPushButton("Remove", self.widget)
            remove_button.clicked.connect(partial(self.remove_person_func, i))
            remove_button.setToolTip(f"Remove {person} from the people list")

            self.widgets.append([person_label, remove_button])
        add_grid_to_layout(self.widgets, layout)
        self.widget.setLayout(layout)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
