from PyQt5 import QtWidgets, QtCore

from ui import MediaListScrollArea
from ui import media_objects


class MediaListWidget(QtWidgets.QWidget):
    """The Media List Widget is the widget that holds the buttons for the
    list of Media in the application.

    The functions sent here are sent directly to the Scroll Area object

    :keyword edit_media_func: The function to use when editing one Media
    :keyword remove_media_func: The function to use when remove one Media
    """

    def __init__(self, parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags(),
                 edit_media_func: callable = None, remove_media_func: callable = None):
        super().__init__(parent, flags)

        # Create the Scroll Area
        self.scroll_area = MediaListScrollArea(
            self, edit_media_func=edit_media_func,
            remove_media_func=remove_media_func,
            update_stats_func=self.update_stats
        )
        self.scroll_area.setAlignment(QtCore.Qt.AlignHCenter)

        # Create the widget attributes for inside the Media List Widget
        self.start_finish_combobox = None
        self.type_combobox = None
        self.provider_combobox = None
        self.person_combobox = None

        # Create the widget attributes for the count and runtime stats
        self.percent_started_label = None
        self.percent_finished_label = None
        self.count_label = None
        self.runtime_label = None

        self.setup_ui()

    def setup_ui(self):
        """Sets up the UI for the Media List Widget"""

        layout = QtWidgets.QGridLayout()

        self.percent_started_label = QtWidgets.QLabel(self)
        self.percent_finished_label = QtWidgets.QLabel(self)
        self.count_label = QtWidgets.QLabel(self)
        self.runtime_label = QtWidgets.QLabel(self)
        self.update_stats()

        layout.addWidget(self.scroll_area, 0, 0, 1, 4)
        layout.addWidget(self.percent_started_label, 1, 0)
        layout.addWidget(self.percent_finished_label, 1, 1)
        layout.addWidget(self.runtime_label, 1, 2)
        layout.addWidget(self.count_label, 1, 3)

        self.setLayout(layout)

    def update_stats(self):
        """Updates the stats at the bottom of the widget
        for how many Media show up and the total runtime.
        """
        total_media = len(media_objects.get_filtered_media())
        started_media = len([
            media
            for media in media_objects.get_filtered_media()
            if media.is_started()
        ])
        finished_media = len([
            media
            for media in media_objects.get_filtered_media()
            if media.is_finished()
        ])
        weeks, days = divmod(sum([
            media.get_runtime()
            for media in media_objects.get_filtered_media()
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
        ])

        self.percent_started_label.setText("{}% Started".format(
            round(started_media / total_media * 100, 2)
        ))
        self.percent_finished_label.setText("{}% Finished".format(
            round(finished_media / total_media * 100, 2)
        ))
        self.runtime_label.setText(f"Runtime: {runtime_text}")
        self.count_label.setText("Count: {}".format(
            len(media_objects.get_filtered_media())
        ))
