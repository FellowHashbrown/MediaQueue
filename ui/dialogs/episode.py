import sys
from datetime import datetime
from typing import Union

from PyQt5 import QtWidgets

from media import Episode
from ui import MessageBox, add_grid_to_layout
from ui import media_objects


class EpisodeDialog(QtWidgets.QDialog):
    """The Episode Dialog handles a user adding an Episode
    to a Limited Series, a TV Show, or a Podcast

    The user will enter in the Season number, if applicable, the
    """

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, show_season: Union[bool, None] = True):
        super().__init__(parent)
        self.show_season = show_season

        self.button_box_add = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.button_box_edit = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save)

        self.button_box_add.accepted.connect(self.add)
        self.button_box_add.rejected.connect(self.cancel)
        self.button_box_edit.accepted.connect(self.add)
        self.button_box_edit.rejected.connect(self.cancel)

        self.season_spinner = None
        self.episode_spinner = None
        self.name_line_edit = None
        self.runtime_spinner = None
        self.watched_checkbox = None

        self.month_combobox = None
        self.day_spinner = None

        self.setup_ui()
        self.result = self.exec_()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def setup_ui(self):
        """Sets up the UI and layout of the Episode dialog"""

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.setup_episode_ui(self))
        if media_objects.get_episode() is not None:
            layout.addWidget(self.button_box_edit)
            self.window().setWindowTitle(f"Edit {media_objects.get_episode().get_name()}")
        else:
            layout.addWidget(self.button_box_add)
            self.window().setWindowTitle("Add Episode")

        self.setLayout(layout)
        self.show()

    def setup_episode_ui(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """Creates and returns the widgets for the Episode widgets
        such as the Season spinner, Episode spinner, Name Entry, Runtime Spinner,
        and Watched checkbox.

        :param parent: The parent widget of the Episode widgets
        """

        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QGridLayout()

        season_label = QtWidgets.QLabel("Season" if self.show_season is not None else "Year", widget)
        name_label = QtWidgets.QLabel("Name", widget)
        runtime_label = QtWidgets.QLabel("Runtime (in minutes)", widget)

        if self.show_season is not None:
            episode_label = QtWidgets.QLabel("Episode", widget)
            month_label = day_label = None
        else:
            month_label = QtWidgets.QLabel("Month", widget)
            day_label = QtWidgets.QLabel("Day", widget)
            episode_label = None

        self.season_spinner = QtWidgets.QSpinBox(widget)
        self.name_line_edit = QtWidgets.QLineEdit(widget)
        self.name_line_edit.setPlaceholderText("Episode Name")
        self.name_line_edit.selectAll()
        self.runtime_spinner = QtWidgets.QSpinBox(widget)
        self.runtime_spinner.setRange(1, 1000)
        self.watched_checkbox = QtWidgets.QCheckBox("Watched?", widget)

        if self.show_season is not None:
            self.season_spinner.setRange(1, 10000)
            self.episode_spinner = QtWidgets.QSpinBox(widget)
            self.episode_spinner.setRange(1, 1000)
        else:
            self.season_spinner.setRange(1900, datetime.now().year)
            self.season_spinner.setValue(datetime.now().year)
            self.season_spinner.valueChanged.connect(self.update_podcast_widgets)

            self.month_combobox = QtWidgets.QComboBox(widget)
            self.month_combobox.addItems(["January", "February", "March", "April", "May", "June",
                                          "July", "August", "September", "October", "November", "December"])
            self.month_combobox.setCurrentIndex(datetime.now().month)
            self.month_combobox.currentIndexChanged.connect(self.update_podcast_widgets)

            self.day_spinner = QtWidgets.QSpinBox(widget)
            self.day_spinner.setRange(1, 31)
            self.day_spinner.setValue(datetime.now().day)

        episode = media_objects.get_episode()
        if episode is not None:
            self.season_spinner.setValue(episode.get_season())
            self.name_line_edit.setText(episode.get_name())
            self.runtime_spinner.setValue(episode.get_runtime())
            self.watched_checkbox.setChecked(episode.is_watched())

            if self.show_season is not None:
                self.episode_spinner.setValue(episode.get_episode())
            else:
                self.month_combobox.setCurrentIndex(episode.get_episode() // 1000)
                self.day_spinner.setValue(episode.get_episode() % 1000)

        if self.show_season is not None:
            grid = [[season_label, self.season_spinner],
                    [episode_label, self.episode_spinner],
                    [name_label, self.name_line_edit],
                    [runtime_label, self.runtime_spinner],
                    [self.watched_checkbox]]
        else:
            grid = [[season_label, self.season_spinner],
                    [month_label, self.month_combobox],
                    [day_label, self.day_spinner],
                    [name_label, self.name_line_edit],
                    [runtime_label, self.runtime_spinner],
                    [self.watched_checkbox]]

        if self.show_season is False:
            _ = grid.pop(0)
            season_label.setVisible(False)
            self.season_spinner.setVisible(False)

        add_grid_to_layout(grid, layout)
        widget.setLayout(layout)
        return widget

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_podcast_widgets(self):
        """Updates the episode widgets and their values
        whenever a Podcast episode is being added or edited
        """

        day_max = [
            31, 29 if self.season_spinner.value() % 4 == 0 else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31
        ]
        max_day_value = day_max[self.month_combobox.currentIndex()]

        self.day_spinner.setRange(1, max_day_value)
        if self.day_spinner.value() > max_day_value:
            self.day_spinner.setValue(max_day_value)

    def clear_widgets(self):
        """Clears the widgets completely in the EpisodeDialog"""

        self.season_spinner.setValue(1)
        self.name_line_edit.setText("")
        self.runtime_spinner.setValue(1)
        self.watched_checkbox.setChecked(False)

        if self.show_season is not None:
            self.episode_spinner.setValue(1)
        else:
            self.month_combobox.setCurrentIndex(datetime.now().month)
            self.day_spinner.setValue(datetime.now().day)

    def cancel(self):
        """Cancels creating or editing an Episode"""
        self.clear_widgets()
        self.reject()

    def add(self):
        """Creates the episode object from the widget values

        If a value is invalid in the Episode object,
        a Message Box will appear saying that something is wrong
        """

        try:
            if self.show_season is not None:
                episode_value = self.episode_spinner.value()
            else:
                episode_value = self.month_combobox.currentIndex() * 1000 + self.day_spinner.value()
            media_objects.set_episode(Episode(
                self.season_spinner.value() if self.show_season is not False else 1,
                episode_value,
                self.name_line_edit.text() or None,
                self.runtime_spinner.value(),
                watched=self.watched_checkbox.isChecked()
            ))
            self.clear_widgets()
            self.accept()
        except ValueError:
            MessageBox("Missing Values",
                       "You must specify the Name of the episode",
                       self.parent())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    EpisodeDialog()
    print(media_objects.get_episode())
