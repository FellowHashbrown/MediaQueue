from functools import partial
from typing import Union

from PyQt5 import QtWidgets, QtCore

from ui import add_grid_to_layout
from ui import media_objects


class EpisodeListScrollArea(QtWidgets.QScrollArea):
    """The Episode List Scroll Area is the Scroll Area
    meant to display all the Episodes in a Podcast, TV Show, or Limited Series

    :keyword edit_episode_func: The function to use when editing an Episode
    :keyword remove_episode_func: The function to use when removing an Episode
    :keyword hide_season: Whether or not to hide the season label from the Episode dialog
    """

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, edit_episode_func: callable = None, remove_episode_func: callable = None,
                 hide_season: Union[bool, None] = False, update_season_func: callable = None):
        super().__init__(parent)

        # Save the parameters as attributes
        self.hide_season = hide_season
        self.edit_episode_func = edit_episode_func
        self.remove_episode_func = remove_episode_func
        self.update_season_func = update_season_func

        # Create the widget attributes for inside the scroll area
        self.widget = None
        self.widgets = None
        self.no_episodes_label = None

        self.update_ui()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_ui(self):
        """Creates/Updates the UI for the List of Episodes"""
        value_y = self.verticalScrollBar().value()
        value_x = self.horizontalScrollBar().value()

        # Setup the widgets and labels for the Scroll Area
        self.widget = QtWidgets.QWidget(self.parent())
        layout = QtWidgets.QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.no_episodes_label = QtWidgets.QLabel("No Episodes", self)
        self.no_episodes_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.widgets = [[
            QtWidgets.QLabel("Watched?", self), QtWidgets.QLabel("Season", self),
            QtWidgets.QLabel("Episode", self), QtWidgets.QLabel("Runtime", self),
            QtWidgets.QLabel("Name", self)
        ]]
        for widget in self.widgets[0]:
            widget.setStyleSheet("font-weight: bold;")
            if widget.text() == "Name":
                widget.setAlignment(QtCore.Qt.AlignHCenter)
        if self.hide_season is True:
            self.widgets[0][1].hide()
            self.widgets[0].pop(1)  # Remove the season column label from the widget grid
        elif self.hide_season is None:
            self.widgets[0][1].setText("Year")

        # Sort the episodes and create the widgets for the Episodes
        media_objects.sort_episodes()
        episodes = media_objects.get_episodes()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for i in range(len(episodes)):
            episode = episodes[i]

            watched_checkbox = QtWidgets.QCheckBox(self)
            watched_checkbox.clicked.connect(partial(self.update_watched, i))
            watched_checkbox.setChecked(episode.is_watched())
            watched_checkbox.setToolTip(f"Set the watched status of {episode.get_name()}")

            season_label = QtWidgets.QLabel(str(episode.get_season()), self)
            episode_label = QtWidgets.QLabel(str(episode.get_episode())
                                             if self.hide_season is not None
                                             else str("%s %s" % (months[episode.get_episode() // 1000 - 1],
                                                                 episode.get_episode() % 1000)), self)
            runtime_label = QtWidgets.QLabel("{} min{}".format(
                episode.get_runtime(),
                "s" if episode.get_runtime() != 1 else ""
            ), self)

            episode_button = QtWidgets.QPushButton(episode.get_name().replace("&", "&&"), self)
            episode_button.clicked.connect(partial(self.edit_episode_func, i))
            episode_button.setToolTip(f"Edit {episode.get_name()}")

            remove_button = QtWidgets.QPushButton("Remove", self)
            remove_button.clicked.connect(partial(self.remove_episode_func, i))
            remove_button.setToolTip(f"Remove {episode.get_name()} from the episode list")

            episode_widgets = [watched_checkbox, season_label,
                               episode_label, runtime_label,
                               episode_button, remove_button]
            if self.hide_season:
                episode_widgets[1].hide()
                episode_widgets.pop(1)  # Remove the season label from the widget grid
            self.widgets.append(episode_widgets)

        # Add all the widgets to the layout, set the layout
        #   and filter the widgets
        add_grid_to_layout(self.widgets, layout)
        layout.addWidget(self.no_episodes_label, 1, 0, 1, 5 if self.hide_season else 6)

        self.widget.setLayout(layout)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.filter()
        self.verticalScrollBar().setValue(value_y)
        self.horizontalScrollBar().setValue(value_x)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_watched(self, index: int):
        """Updates the watched attribute of the Episode
        at the specified index

        :param index: The index of the Episode to edit
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        watched = self.widgets[index + 1][0].isChecked()
        media_objects.get_episodes()[index].set_watched(watched)
        self.update_season_func()
        self.filter()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def filter(self):
        """Filters the Episodes in the ScrollArea"""
        filtered_episodes = media_objects.get_filtered_episodes()

        # Set the visibility of the widgets
        #   based off the filtered episodes
        for i in range(len(media_objects.get_episodes())):
            for ew in self.widgets[i + 1]:
                ew.setVisible(media_objects.get_episodes()[i] in filtered_episodes)
        self.no_episodes_label.setVisible(len(filtered_episodes) == 0)
