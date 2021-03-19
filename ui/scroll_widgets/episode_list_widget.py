from functools import partial
from typing import Union

from PyQt5 import QtWidgets, QtCore

from ui import EpisodeListScrollArea
from ui import media_objects


class EpisodeListWidget(QtWidgets.QWidget):
    """The Episode List Widget is the widget that holds the
    filters for the episodes, the add button, and the scroll area for the
    Episode list.

    The functions sent here are sent directly to the Scroll Area object

    :keyword edit_episode_func: The function to use when editing an Episode
    :keyword remove_episode_func: The function to use when removing an Episode
    :keyword hide_season: Whether or not to hide the season label from the Episode dialog
    """

    def __init__(self, parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags(),
                 *, edit_episode_func: callable = None, remove_episode_func: callable = None,
                 hide_season: Union[bool, None] = False):
        super().__init__(parent, flags)
        self.edit_episode_func = edit_episode_func
        self.remove_episode_func = remove_episode_func
        self.hide_season = hide_season

        # Create the Scroll Area
        self.scroll_area = EpisodeListScrollArea(
            self, edit_episode_func=edit_episode_func,
            remove_episode_func=remove_episode_func,
            hide_season=hide_season)
        self.scroll_area.setAlignment(QtCore.Qt.AlignHCenter)

        # Create the widget attributes for inside the Episode List Widget
        self.filter_combobox = None
        self.add_episode_button = None
        self.filter_options = None

        # Create the widget attributes for the count and runtime stats
        self.percent_watched_label = None
        self.percent_unwatched_label = None
        self.count_label = None
        self.runtime_label = None

        self.setup_ui()

    def setup_ui(self):
        """Sets up the UI for the Episode List Widget"""

        def filter_function():
            """Loads in the filter combobox index and sets the
            filter options accordingly
            """

            index = self.filter_combobox.currentIndex()
            season = None
            watched = None
            if index >= 3:
                _, season = self.filter_combobox.currentText().split()
                season = int(season)
            if index == 1:
                watched = True
            elif index == 2:
                watched = False
            media_objects.set_episode_filters(season=season, watched=watched)
            self.scroll_area.filter()
            self.update_stats()

        # Sets the layout for the widget, create the combo boxes
        #   and adds the child widgets to this widget
        layout = QtWidgets.QGridLayout()

        self.percent_watched_label = QtWidgets.QLabel(self)
        self.percent_unwatched_label = QtWidgets.QLabel(self)
        self.count_label = QtWidgets.QLabel(self)
        self.runtime_label = QtWidgets.QLabel(self)
        self.update_stats()

        self.filter_combobox = QtWidgets.QComboBox(self)
        self.filter_combobox.currentIndexChanged.connect(filter_function)
        self.update_filter_options()

        self.add_episode_button = QtWidgets.QPushButton("Add Episode", self)
        self.add_episode_button.clicked.connect(partial(self.edit_episode_func, None))

        layout.addWidget(self.filter_combobox, 0, 0, 1, 3)
        layout.addWidget(self.add_episode_button, 0, 3)
        layout.addWidget(self.scroll_area, 1, 0, 3, 4)
        layout.addWidget(self.percent_watched_label, 5, 0)
        layout.addWidget(self.percent_unwatched_label, 5, 1)
        layout.addWidget(self.runtime_label, 5, 2)
        layout.addWidget(self.count_label, 5, 3)

        self.setLayout(layout)

    def update_stats(self):
        """Updates the stats at the bottom of the widget
        for how many Episodes show up and the total runtime
        """
        total_episodes = len(media_objects.get_filtered_episodes())
        watched_episodes = len([
            episode
            for episode in media_objects.get_filtered_episodes()
            if episode.is_watched()
        ])
        unwatched_episodes = len([
            episode
            for episode in media_objects.get_filtered_episodes()
            if not episode.is_watched()
        ])
        weeks, days = divmod(sum([
            episode.get_runtime()
            for episode in media_objects.get_filtered_episodes()
        ]), 7 * 24 * 60)
        days, hours = divmod(days, 24 * 60)
        hours, minutes = divmod(hours, 60)
        runtime_stats = {
            "wks": weeks, "days": days,
            "hours": hours, "mins": minutes
        }
        runtime_text = " ".join([
            f"{runtime_stats[stat]}{stat[:-1]}"
            if runtime_stats[stat] == 1
            else f"{runtime_stats[stat]}{stat}"
            for stat in runtime_stats
            if runtime_stats[stat] > 0
        ])

        self.percent_watched_label.setText("{}% Watched".format(
            round(watched_episodes / total_episodes * 100, 2)
            if total_episodes != 0 else 0))
        self.percent_unwatched_label.setText("{}% Unwatched".format(
            round(unwatched_episodes / total_episodes * 100, 2)
            if total_episodes != 0 else 0))
        self.runtime_label.setText(f"Runtime: {runtime_text}")
        self.count_label.setText("Count: {}".format(
            len(media_objects.get_filtered_episodes())))

    def update_filter_options(self):
        """Updates the filter options based off the episodes in the widget"""

        self.filter_options = ["All Episodes", "Seen Episodes", "Unseen Episodes"]

        # Create a list of seasons to add to the filter options
        #   by going through the episodes and the unique season numbers
        #   Only if the seasons will not be hidden (like in Limited Series)
        if self.hide_season is not True:

            seasons = []
            for episode in media_objects.get_episodes():
                if episode.get_season() not in seasons:
                    seasons.append(episode.get_season())
            for season in sorted(seasons):
                self.filter_options.append("{}{}".format("Season " if self.hide_season is False else "", season))

        # Clear the current items and update the filter options
        self.filter_combobox.clear()
        self.filter_combobox.addItems(self.filter_options)
        self.filter_combobox.setCurrentIndex(0)
