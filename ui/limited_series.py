import sys
from functools import partial

from PyQt5 import QtWidgets, QtCore

from media import StreamingProvider, Person, LimitedSeries
from ui import MessageBox, add_grid_to_layout, EpisodeDialog, EpisodeListWidget
from ui import media_objects


class LimitedSeriesView(QtWidgets.QFrame):
    """The Limited Series view is meant for the editing or addition
    of Limited Series objects in the Media Queue. It is almost identical
    to the TV Show and Podcast views with the exception of the names set for
    the placeholder text and the window title
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
        """Sets up the UI for the Limited Series view"""

        # Create the layout and add the child widgets
        layout = QtWidgets.QVBoxLayout()
        self.episodes_widget = EpisodeListWidget(
            self,
            edit_episode_func=self.add_edit_episode,
            remove_episode_func=self.remove_episode,
            hide_season=True)
        layout.addWidget(self.setup_limited_series_ui(self))
        layout.addWidget(self.episodes_widget, 3)
        layout.addWidget(self.setup_finish_buttons_ui(self))

        self.setLayout(layout)
        self.show()

    def setup_limited_series_ui(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """Sets up the UI for the widgets that allow editing a Limited Series

        :param parent: The parent widget for the widgets created in this function
        """

        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QGridLayout()

        name_label = QtWidgets.QLabel("Name", widget)
        provider_label = QtWidgets.QLabel("Streaming Provider", widget)
        person_label = QtWidgets.QLabel("Person", widget)
        self.start_checkbox = QtWidgets.QCheckBox("Started?", widget)
        self.start_checkbox.clicked.connect(self.update_start)
        self.finish_checkbox = QtWidgets.QCheckBox("Finished?", widget)
        self.finish_checkbox.clicked.connect(self.update_finish)
        divider = QtWidgets.QFrame(widget)
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.name_line_edit = QtWidgets.QLineEdit(widget)
        self.name_line_edit.setPlaceholderText("Limited Series Name")
        self.provider_dropdown = QtWidgets.QComboBox(widget)
        self.provider_dropdown.addItems([provider.value for provider in StreamingProvider])
        self.person_dropdown = QtWidgets.QComboBox(widget)
        self.person_dropdown.addItems([person.value for person in Person])

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

        :param parent: The parent widget for all the widgets created in this view
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
        """Updates the start and finish checkboxes for the Limited Series.

        If a user checks the start checkbox, the finish checkbox will be unchecked
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        started = self.start_checkbox.isChecked()
        finished = self.finish_checkbox.isChecked()
        if started and finished:
            self.finish_checkbox.setChecked(False)
        media_objects.get_limited_series().set_started(started)

    def update_finish(self):
        """Updates the start and finish checkboxes for the Limited Series.

        If a user checks the finish checkbox, the start checkbox will be unchecked.
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        finished = self.start_checkbox.isChecked()
        started = self.finish_checkbox.isChecked()
        if finished and started:
            self.start_checkbox.setChecked(False)
        media_objects.get_limited_series().set_finished(finished)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def clear_widgets(self):
        """Clears the widgets for the Limited Series and clears the attributes"""

        self.name_line_edit.setText("")
        self.provider_dropdown.setCurrentIndex(0)
        self.person_dropdown.setCurrentIndex(0)
        self.episodes_widget.scroll_area.update_ui()

    def cancel(self):
        """Cancels adding or editing a Limited Series and moves back to the previous screen"""

        self.clear_widgets()
        self.callback(canceled=True)

    def add(self, is_saving: bool = False):
        """Saves the current Limited Series as an object and loads it into the
        Media Queue app.

        If the is_saving parameter is set to true, it will retrieve
        the ID of the existing LimitedSeries object so a new file is not made
        with the same data but different ID.

        :param is_saving: Whether or not the addition of this Limited Series
            is actually saving an existing one
        """

        try:

            # Create a new Limited Series object
            #   getting the ID of the limited series, if editing
            if is_saving:
                limited_series = media_objects.get_limited_series()
                id = limited_series.get_id()
            limited_series = LimitedSeries(
                self.name_line_edit.text(),
                self.provider_dropdown.currentText(),
                self.person_dropdown.currentText(),
                [episode for episode in media_objects.get_episodes()],
                started=self.start_checkbox.isChecked(),
                finished=self.finish_checkbox.isChecked()
            )
            if is_saving:
                limited_series.set_id(id)
            media_objects.set_limited_series(limited_series)

            # Save the Limited Series into a file and go back to the previous screen
            limited_series.save()
            self.clear_widgets()
            self.callback(self.index)

        except ValueError:
            MessageBox(
                "Missing Values",
                "You must specify the Name, the Streaming Provider and the Person")

    def edit(self, callback: callable = None, index: int = None):
        """Sets whether the user is editing or adding a Limited Series in this view

        :param callback: The callback function when the user is done editing
        :param index: The index of the Limited Series in the media list
        """

        limited_series = media_objects.get_limited_series()
        self.callback = callback
        self.index = index

        self.add_button.setVisible(limited_series is None)
        self.save_button.setVisible(limited_series is not None)

        if limited_series is not None:
            media_objects.set_episodes([episode for episode in limited_series.get_episodes()])
            self.window().setWindowTitle(f"Edit {limited_series.get_name()}")
            self.name_line_edit.setText(limited_series.get_name())
            self.provider_dropdown.setCurrentText(limited_series.get_provider().value)
            self.person_dropdown.setCurrentText(limited_series.get_person().value)
            self.start_checkbox.setChecked(limited_series.is_started())
            self.finish_checkbox.setChecked(limited_series.is_finished())
            self.episodes_widget.scroll_area.update_ui()
            self.episodes_widget.update_filter_options()
        else:
            self.window().setWindowTitle("Add Limited Series")

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
        episode_dialog = EpisodeDialog(self, show_season=False)

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
        """Allows a user to remove an Episode from the Limited Series

        :param index: The index of the Episode to edit, if any
        """

        if index is not None:
            _ = media_objects.episodes.pop(index)
            media_objects.get_removed_episodes().append(index)
            self.episodes_widget.scroll_area.filter()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = LimitedSeriesView()
    widget.edit(LimitedSeries("iCarly", "Vudu", "Both"))
    sys.exit(app.exec_())
