from PyQt5 import QtWidgets, QtCore

from ui import MessageBox, PersonListScrollArea
from options import options


class PersonDialog(QtWidgets.QDialog):
    """The Person Dialog allows a user to specify the Persons
    they want in the Media Queue.

    There are 2 default ones including Unavailable and Default which cannot be removed.
    """

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, update_func: callable = None):
        super().__init__(parent)
        self.update_func = update_func
        avail_geo = QtWidgets.QDesktopWidget().availableGeometry()
        center = avail_geo.center()

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignHCenter)

        self.setWindowTitle("Configure People")
        self.scroll_area = PersonListScrollArea(self, remove_person_func=self.remove_person)
        self.add_button = QtWidgets.QPushButton("Add Person", self)
        self.add_button.clicked.connect(self.ask_for_person)
        self.add_button.setToolTip("Add a new person to the person list")

        layout.addWidget(self.scroll_area)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

        self.setGeometry((center.x() - (2 * avail_geo.width() // 5) // 2),
                         (center.y() - (2 * avail_geo.height() // 5) // 2),
                         2 * avail_geo.width() // 5,
                         2 * avail_geo.height() // 5)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def ask_for_person(self):
        """Asks the user for a new Person to add to the Person list"""
        person, accepted = QtWidgets.QInputDialog.getText(
            self, "New Person",
            "Enter the person's name: ")
        if accepted:
            if options.add_person(person):
                self.update_func()
                self.scroll_area.update_ui()
            else:
                MessageBox("Person Exists!",
                           f"\"{person}\" already exists in the app.",
                           self)

    def remove_person(self, index: int):
        """Removes a Person from the person list

        :param index: The index of the Person to remove
        """
        if options.remove_person(index):
            self.update_func()
            self.scroll_area.update_ui()
        else:
            MessageBox("Can't Remove That!",
                       (
                        "If you tried removing Default, you can't do that.\n" +
                        "If you were trying to remove something else, then this is a bug and you should report it!\n" +
                        "Check under the Help menu for that!"
                       ),
                       self)
