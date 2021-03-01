import sys
from functools import partial
from PyQt5 import QtWidgets, QtCore

from media import Movie
from ui import MessageBox, add_grid_to_layout


class MovieView(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.movie = None
        self.callback = None
        self.index = None

        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                           QtWidgets.QSizePolicy.MinimumExpanding)
        layout = QtWidgets.QGridLayout()

        name_label = QtWidgets.QLabel("Name", self)
        runtime_label = QtWidgets.QLabel("Runtime (in minutes)", self)
        provider_label = QtWidgets.QLabel("Streaming Provider", self)
        person_label = QtWidgets.QLabel("Person", self)

        self.name_line_edit = QtWidgets.QLineEdit(self)
        self.runtime_spinner = QtWidgets.QSpinBox(self)
        self.runtime_spinner.setRange(0, 1000)
        self.provider_dropdown = QtWidgets.QComboBox(self)
        self.provider_dropdown.addItems(["Vudu", "Disney+", "Netflix", "Hulu", "HBO Max"])
        self.person_dropdown = QtWidgets.QComboBox(self)
        self.person_dropdown.addItems(["Jonah", "Taylor", "Both"])

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(partial(self.add, True))
        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.clicked.connect(self.add)
        self.start_checkbox = QtWidgets.QCheckBox("Started?", self)
        self.finish_checkbox = QtWidgets.QCheckBox("Finished?", self)

        grid = [[name_label, self.name_line_edit, None],
                [runtime_label, self.runtime_spinner, None],
                [provider_label, self.provider_dropdown, None],
                [person_label, self.person_dropdown, None],
                [self.start_checkbox, self.finish_checkbox],
                [None, None]]

        add_grid_to_layout(grid, layout)
        layout.addWidget(self.cancel_button, 5, 0)
        layout.addWidget(self.add_button, 5, 2)
        layout.addWidget(self.save_button, 5, 2)
        layout.setRowStretch(4, 1)

        self.setLayout(layout)
        self.show()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def cancel(self):
        """Resets the values for each widget and returns to the previous widget"""
        self.name_line_edit.setText("")
        self.runtime_spinner.setValue(0)
        self.provider_dropdown.setCurrentIndex(0)
        self.person_dropdown.setCurrentIndex(0)
        self.callback()

    def add(self, is_saving: bool = False):
        """Saves the current Movie as an object and loads it into the
        Media Queue app
        """
        try:
            if is_saving:
                id = self.movie.get_id()
            self.movie = Movie(
                self.name_line_edit.text(),
                self.runtime_spinner.value(),
                self.provider_dropdown.currentText(),
                self.person_dropdown.currentText(),
                started=self.start_checkbox.isChecked(),
                finished=self.finish_checkbox.isChecked()
            )
            if is_saving:
                self.movie.set_id(id)
            self.movie.save()
            self.callback(self.index, self.movie)
        except ValueError:
            MessageBox(
                "Missing Values",
                "You must specify the Name, Runtime, Provider, and Person to create or save a Movie")

    def edit(self, movie: Movie = None, callback: callable = None, index: int = None):
        """Sets whether the user is editing or adding a Movie in this view

        :param movie: The Movie the user is editing, if any
        :param callback: The callback function when the user is done editing
        :param index: The index of the Movie in the media list
        """
        self.movie = movie
        self.callback = callback
        self.index = index

        self.add_button.setVisible(movie is None)
        self.save_button.setVisible(movie is not None)

        if movie is not None:
            self.window().setWindowTitle(f"Edit {movie.get_name()}")
            self.name_line_edit.setText(movie.get_name())
            self.runtime_spinner.setValue(movie.get_runtime())
            self.provider_dropdown.setCurrentText(movie.get_provider().value)
            self.person_dropdown.setCurrentText(movie.get_person().value)
            self.start_checkbox.setChecked(movie.is_started())
            self.finish_checkbox.setChecked(movie.is_finished())
        else:
            self.window().setWindowTitle("Add Movie")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MovieView()
    sys.exit(app.exec_())
