import sys
from functools import partial
from PyQt5 import QtWidgets, QtCore

from media import Movie
from ui import MessageBox, add_grid_to_layout, media_objects
from options import options


class MovieDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.index = None

        self.button_box_add = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.button_box_edit = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)

        self.button_box_add.accepted.connect(partial(self.add, False))
        self.button_box_add.rejected.connect(self.reject)
        self.button_box_edit.accepted.connect(partial(self.add, True))
        self.button_box_edit.rejected.connect(self.reject)

        self.name_line_edit = None
        self.hours_spinner = None
        self.minutes_spinner = None
        self.provider_dropdown = None
        self.person_dropdown = None
        self.start_checkbox = None
        self.finish_checkbox = None

        self.setup_ui()
        self.result = self.exec_()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def setup_ui(self):

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.setup_movie_ui(self))
        if media_objects.get_movie() is not None:
            layout.addWidget(self.button_box_edit)
            self.window().setWindowTitle(f"Edit {media_objects.get_movie().get_name()}")
        else:
            layout.addWidget(self.button_box_add)
            self.window().setWindowTitle("Add Movie")

        self.setLayout(layout)
        self.show()

    def setup_movie_ui(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """Creates and returns the widgets for the Movie widgets
        such as the Name Entry, Runtime spinner, Provider box, and Person box

        :param parent: The parent widget of the Movie widgets
        """

        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QGridLayout()

        name_label = QtWidgets.QLabel("Name", widget)
        runtime_label = QtWidgets.QLabel("Runtime", widget)
        hours_label = QtWidgets.QLabel("Hours", widget)
        minutes_label = QtWidgets.QLabel("Minutes", widget)
        provider_label = QtWidgets.QLabel("Streaming Provider", widget)
        person_label = QtWidgets.QLabel("Person", widget)

        self.name_line_edit = QtWidgets.QLineEdit(widget)
        self.name_line_edit.setPlaceholderText("Movie Name")
        self.name_line_edit.setToolTip("The name for the Movie")

        self.hours_spinner = QtWidgets.QSpinBox(widget)
        self.hours_spinner.setRange(0, 20)
        self.hours_spinner.setToolTip("The hours portion of the runtime of the Movie")

        self.minutes_spinner = QtWidgets.QSpinBox(widget)
        self.minutes_spinner.setRange(0, 59)
        self.minutes_spinner.setToolTip("The minutes portion of the runtime of the Movie")

        self.provider_dropdown = QtWidgets.QComboBox(widget)
        self.provider_dropdown.addItems([provider for provider in options.get_providers()])
        self.provider_dropdown.setToolTip("The Streaming Provider for the Movie")

        self.person_dropdown = QtWidgets.QComboBox(widget)
        self.person_dropdown.addItems([person for person in options.get_persons()])
        self.person_dropdown.setToolTip("The Person watching the Movie")

        self.start_checkbox = QtWidgets.QCheckBox("Started?", widget)
        self.start_checkbox.clicked.connect(self.update_start)
        self.start_checkbox.setToolTip("Mark the Movie as started")

        self.finish_checkbox = QtWidgets.QCheckBox("Finished?", widget)
        self.finish_checkbox.clicked.connect(self.update_finish)
        self.finish_checkbox.setToolTip("Mark the Movie as finished")

        movie = media_objects.get_movie()
        if movie is not None:
            hours, minutes = divmod(movie.get_runtime(), 60)
            self.name_line_edit.setText(movie.get_name())
            self.hours_spinner.setValue(hours)
            self.minutes_spinner.setValue(minutes)
            self.provider_dropdown.setCurrentText(movie.get_provider())
            self.person_dropdown.setCurrentText(movie.get_person())
            self.start_checkbox.setChecked(movie.is_started())
            self.finish_checkbox.setChecked(movie.is_finished())

        grid = [[name_label, self.name_line_edit, None, None, None],
                [runtime_label, self.hours_spinner, hours_label, self.minutes_spinner, minutes_label],
                [provider_label, self.provider_dropdown, None, None, None],
                [person_label, self.person_dropdown, None, None, None],
                [self.start_checkbox, self.finish_checkbox]]

        add_grid_to_layout(grid, layout)
        widget.setLayout(layout)
        return widget

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_start(self):
        """Updates the start and finish checkboxes for the Movie.

        If a user checks the start checkbox, the finish checkbox will be unchecked
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        started = self.start_checkbox.isChecked()
        finished = self.finish_checkbox.isChecked()
        if started and finished:
            self.finish_checkbox.setChecked(False)
        if media_objects.get_movie() is not None:
            media_objects.get_movie().set_started(started)

    def update_finish(self):
        """Updates the start and finish checkboxes for the Movie.

        If a user checks the finish checkbox, the start checkbox will be unchecked.
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        finished = self.start_checkbox.isChecked()
        started = self.finish_checkbox.isChecked()
        if finished and started:
            self.start_checkbox.setChecked(False)
        if media_objects.get_movie() is not None:
            media_objects.get_movie().set_finished(finished)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def clear_widgets(self):
        """Cleats the widgets for the Movie and clears the attributes"""

        self.name_line_edit.setText("")
        self.hours_spinner.setValue(0)
        self.minutes_spinner.setValue(0)
        self.provider_dropdown.setCurrentIndex(0)
        self.person_dropdown.setCurrentIndex(0)
        self.start_checkbox.setChecked(False)
        self.finish_checkbox.setChecked(False)

    def add(self, is_saving: bool = False):
        """Creates the movie object from the widget values

        If a value is invalid in the Movie object,
        a Message Box will appear saying that something is wrong
        """
        try:
            if is_saving:
                movie = media_objects.get_movie()
                id = movie.get_id()
            movie = Movie(
                self.name_line_edit.text(),
                self.hours_spinner.value() * 60 + self.minutes_spinner.value(),
                self.provider_dropdown.currentText(),
                self.person_dropdown.currentText(),
                started=self.start_checkbox.isChecked(),
                finished=self.finish_checkbox.isChecked()
            )
            if is_saving:
                movie.set_id(id)
            movie.save()
            media_objects.set_movie(movie)
            self.clear_widgets()
            self.accept()
        except ValueError:
            MessageBox(
                "Missing Values",
                "You must specify the Name, Runtime, Provider, and Person to create or save a Movie")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MovieDialog()
    sys.exit(app.exec_())
