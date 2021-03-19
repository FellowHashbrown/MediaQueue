import sys
from functools import partial

from PyQt5 import QtWidgets, QtCore

from media import Season, Episode, Podcast
from ui import MessageBox, add_grid_to_layout, EpisodeDialog, EpisodeListWidget
from ui import media_objects
from options import options


class PodcastView(QtWidgets.QFrame):
    """The Podcast View is meant for the editing or addition
    of Podcast objects in the Media Queue. It is almost identical
    to the TV Show and Limited Series views with the exception of the names set
    for the placeholder text and the window title
    """

    def __init__(self, parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.callback = None
        self.index = None

        self.episodes_widget = None

        self.start_checkbox = None
        self.finish_checkbox = None

        self.name_line_edit = None
        self.provider_dropdown = None
        self.person_dropdown = None

        self.cancel_button = None
        self.add_button = None
        self.save_button = None

        self.setup_ui()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def setup_ui(self):
        """Sets up the UI for the Podcast view"""

        # Create the layout and add the child widgets
        layout = QtWidgets.QVBoxLayout()
        self.episodes_widget = EpisodeListWidget(
            self,
            edit_episode_func=self.add_edit_episode,
            remove_episode_func=self.remove_episode,
            hide_season=None)
        layout.addWidget(self.setup_podcast_ui(self))
        layout.addWidget(self.episodes_widget, 3)
        layout.addWidget(self.setup_finish_buttons_ui(self))

        self.setLayout(layout)
        self.show()

    def setup_podcast_ui(self, parent: QtWidgets.QWidget):
        """Sets up the UI for the widgets that allow editing a Podcast

        :param parent: The parent widget for the widgets created in this function
        """

        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QGridLayout()

        name_label = QtWidgets.QLabel("Name", widget)
        provider_label = QtWidgets.QLabel("Streaming Provider", widget)
        person_label = QtWidgets.QLabel("Person", widget)
        self.start_checkbox = QtWidgets.QCheckBox("Started?", widget)
        self.finish_checkbox = QtWidgets.QCheckBox("Finished?", widget)
        divider = QtWidgets.QFrame(widget)
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.name_line_edit = QtWidgets.QLineEdit(widget)
        self.name_line_edit.setPlaceholderText("Podcast Name")
        self.provider_dropdown = QtWidgets.QComboBox(widget)
        self.provider_dropdown.addItems([provider for provider in options.get_providers()])
        self.person_dropdown = QtWidgets.QComboBox(widget)
        self.person_dropdown.addItems([person for person in options.get_persons()])

        grid = [[name_label, self.name_line_edit, None],
                [provider_label, self.provider_dropdown, None],
                [person_label, self.person_dropdown, None],
                [self.start_checkbox, self.finish_checkbox],
                [divider, None, None]]

        add_grid_to_layout(grid, layout)
        widget.setLayout(layout)
        return widget

    def setup_finish_buttons_ui(self, parent: QtWidgets.QWidget):
        """Sets up the UI for the finish buttons in the view

        :param parent: The parent widget for all the widgets created in this function
        """

        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QGridLayout()

        self.cancel_button = QtWidgets.QPushButton("Cancel", widget)
        self.cancel_button.clicked.connect(self.cancel)

        self.add_button = QtWidgets.QPushButton("Add", widget)
        self.add_button.clicked.connect(partial(self.add, False))

        self.save_button = QtWidgets.QPushButton("Save", widget)
        self.save_button.clicked.connect(partial(self.add, True))

        layout.addWidget(self.cancel_button, 0, 0)
        layout.addWidget(self.add_button, 0, 2)
        layout.addWidget(self.save_button, 0, 2)

        widget.setLayout(layout)

        return widget

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_start(self):
        """Updates the start and finish checkboxes for the Podcast.

        If a user checks the start checkbox, the finish checkbox will be unchecked
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        started = self.start_checkbox.isChecked()
        finished = self.finish_checkbox.isChecked()
        if started and finished:
            self.finish_checkbox.setChecked(False)
        if media_objects.get_podcast() is not None:
            media_objects.get_podcast().set_started(started)

    def update_finish(self):
        """Updates the start and finish checkboxes for the Podcast.

        If a user checks the finish checkbox, the start checkbox will be unchecked.
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        finished = self.start_checkbox.isChecked()
        started = self.finish_checkbox.isChecked()
        if finished and started:
            self.start_checkbox.setChecked(False)
        if media_objects.get_podcast() is not None:
            media_objects.get_podcast().set_finished(finished)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def clear_widgets(self):
        """Clears the widgets for the Podcast and clears the attributes"""

        media_objects.set_episodes()
        self.name_line_edit.setText("")
        self.provider_dropdown.setCurrentIndex(0)
        self.person_dropdown.setCurrentIndex(0)
        self.episodes_widget.scroll_area.widgets = []
        self.episodes_widget.scroll_area.update_ui()

    def cancel(self):
        """Cancels adding or editing a Podcast and moves back to the previous screen"""

        self.clear_widgets()
        self.callback(canceled=True)

    def add(self, is_saving: bool = False):
        """Saves the current Podcast as an object and loads it into the
        Media Queue app

        If the is_saving parameter is set to true, it will retrieve
        the ID of the existing Podcast object so a new file is not made
        with the same data but different ID

        :param is_saving: Whether or not the addition of this Podcast
            is actually saving an existing one
        """

        try:

            # Get a list of Seasons and Episodes in those Seasons
            seasons = {}
            for episode in media_objects.get_episodes():
                if episode.get_season() not in seasons:
                    seasons[episode.get_season()] = []
                seasons[episode.get_season()].append(episode)

            # Create a new Podcast object
            #   getting the ID of the podcast, if editing
            if is_saving:
                podcast = media_objects.get_podcast()
                id = podcast.get_id()
            podcast = Podcast(
                self.name_line_edit.text(),
                self.provider_dropdown.currentText(),
                self.person_dropdown.currentText(),
                [
                    Season(season, seasons[season])
                    for season in seasons
                ],
                started=self.start_checkbox.isChecked(),
                finished=self.finish_checkbox.isChecked()
            )
            if is_saving:
                podcast.set_id(id)
            media_objects.set_podcast(podcast)

            # Save the Podcast into a file and go back to the previous screen
            podcast.save()
            self.clear_widgets()
            self.callback(self.index)

        except ValueError:
            MessageBox(
                "Missing Values",
                "You must specify the Name, the Streaming Provider and the Person",
                self)

    def edit(self, callback: callable = None, index: int = None):
        """Sets whether the user is editing or adding a Podcast in this view

        :param callback: The callback function when the user is done editing
        :param index: The index of the Podcast in the media list
        """
        podcast = media_objects.get_podcast()
        self.callback = callback
        self.index = index

        self.add_button.setVisible(podcast is None)
        self.save_button.setVisible(podcast is not None)

        if podcast is not None:
            media_objects.set_episodes([
                episode
                for season in podcast.get_seasons()
                for episode in season.get_episodes()])
            self.window().setWindowTitle(f"Edit {podcast.get_name()}")
            self.name_line_edit.setText(podcast.get_name())
            self.provider_dropdown.setCurrentText(podcast.get_provider())
            self.person_dropdown.setCurrentText(podcast.get_person())
            self.start_checkbox.setChecked(podcast.is_started())
            self.finish_checkbox.setChecked(podcast.is_finished())
            self.episodes_widget.scroll_area.update_ui()
            self.episodes_widget.update_filter_options()
            self.episodes_widget.update_stats()
        else:
            self.window().setWindowTitle("Add Podcast")

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def add_edit_episode(self, index: int = None):
        """Allow a user to add or edit an Episode

        :param index: The index of an Episode to edit, if any
        """

        # Ask the Episode Dialog for an Episode input
        if index is None:
            media_objects.set_episode()
        else:
            media_objects.set_episode(media_objects.get_episodes()[index])
        episode_dialog = EpisodeDialog(self, show_season=None)

        # If the Episode dialog result was accepted (Save or Ok)
        #   set the edited Episode or add a new one to the list
        if episode_dialog.result == QtWidgets.QDialog.Accepted:
            episode = media_objects.get_episode()
            if index is not None:
                media_objects.get_episodes()[index] = episode
            else:
                media_objects.get_episodes().append(episode)
            self.episodes_widget.scroll_area.update_ui()
            self.episodes_widget.update_filter_options()

    def remove_episode(self, index: int = None):
        """Allows a user to remove an Episode from the Podcast

        :param index: The index of the Episode to edit, if any
        """

        if index is not None:
            media_objects.get_episodes()[index] = None
            media_objects.get_removed_episodes().append(index)
            self.episodes_widget.scroll_area.filter()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_providers(self):
        """Updates the list of providers in the combobox for providers"""
        self.provider_dropdown.clear()
        self.provider_dropdown.addItems(options.get_providers())

    def update_persons(self):
        """Updates the list of persons in the combobox for persons"""
        self.person_dropdown.clear()
        self.person_dropdown.addItems(options.get_persons())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = PodcastView()
    widget.edit(Podcast("Crime Junkie", "Apple", "Jonah", [
        Season(2020, [Episode(1, 1, "iPilot", 23),
                      Episode(1, 2, "iLike Jake", 23)]),
        Season(2021, [Episode(2, 1, "iSomething", 23),
                      Episode(2, 2, "iAnother", 23)])
    ]))
    sys.exit(app.exec_())
