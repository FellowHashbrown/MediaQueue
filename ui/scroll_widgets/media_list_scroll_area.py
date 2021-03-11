from functools import partial
from PyQt5 import QtWidgets, QtCore

from media.util import get_type
from ui import add_grid_to_layout
from ui import media_objects


class MediaListScrollArea(QtWidgets.QScrollArea):
    """The Media List Scroll area is the Scroll Area
    meant to display Movies, Limited Series, Podcasts, and TV Shows

    :keyword edit_media_func: The function to use when editing one Media
    :keyword remove_media_func: The function to use when removing one Media
    """

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, edit_media_func: callable = None, remove_media_func: callable = None,
                 update_stats_func: callable = None):
        super().__init__(parent)

        # Save the parameters as attributes
        self.edit_media_func = edit_media_func
        self.remove_media_func = remove_media_func
        self.update_stats_func = update_stats_func

        # Create the widget attributes for inside the scroll area
        self.widget = None
        self.widgets = None
        self.no_media_label = None

        self.update_ui()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_ui(self):
        """Creates/updates the UI for the list of Media"""

        # Setup the widgets and labels for the Scroll Area
        self.widget = QtWidgets.QWidget(self.parent())
        layout = QtWidgets.QGridLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.no_media_label = QtWidgets.QLabel("No Media", self)
        self.no_media_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.widgets = [[
            QtWidgets.QLabel("Started?", self), QtWidgets.QLabel("Finished?", self),
            QtWidgets.QLabel("Type", self), QtWidgets.QLabel("Provider", self),
            QtWidgets.QLabel("Person", self), QtWidgets.QLabel("Runtime", self),
            QtWidgets.QLabel("Name", self)
        ]]
        for widget in self.widgets[0]:
            widget.setStyleSheet("font-weight: bold;")
            if widget.text() == "Name":
                widget.setAlignment(QtCore.Qt.AlignHCenter)

        # Sort the media and create the widgets
        media_objects.sort_media()
        media = media_objects.get_media()
        for i in range(len(media)):
            medium = media[i]

            start_checkbox = QtWidgets.QCheckBox(self)
            start_checkbox.clicked.connect(partial(self.update_start, i))
            start_checkbox.clicked.connect(self.update_stats_func)
            start_checkbox.setChecked(medium.is_started())
            start_checkbox.setToolTip(f"Set the started status of {medium.get_name()}")

            finish_checkbox = QtWidgets.QCheckBox(self)
            finish_checkbox.clicked.connect(partial(self.update_finish, i))
            finish_checkbox.clicked.connect(self.update_stats_func)
            finish_checkbox.setChecked(medium.is_finished())
            finish_checkbox.setToolTip(f"Set the finished status of {medium.get_name()}")

            hours, minutes = divmod(medium.get_runtime(), 60)
            type_label = QtWidgets.QLabel(get_type(medium), self)
            provider_label = QtWidgets.QLabel(medium.get_provider(), self)
            person_label = QtWidgets.QLabel(medium.get_person(), self)
            runtime_label = QtWidgets.QLabel("{}hr{} {}min{}".format(
                hours, "s" if hours != 1 else "",
                minutes, "s" if minutes != 1 else ""
            ), self)

            media_button = QtWidgets.QPushButton(medium.get_name().replace("&", "&&"), self)
            media_button.clicked.connect(partial(self.edit_media_func, get_type(medium), i))
            media_button.setToolTip(f"Edit {medium.get_name()}")

            remove_button = QtWidgets.QPushButton("Remove", self)
            remove_button.clicked.connect(partial(self.remove_media_func, i))
            remove_button.setToolTip(f"Remove {medium.get_name()} from the media queue")

            media_widgets = [start_checkbox, finish_checkbox,
                             type_label, provider_label,
                             person_label, runtime_label,
                             media_button, remove_button]
            self.widgets.append(media_widgets)

        add_grid_to_layout(self.widgets, layout)
        layout.addWidget(self.no_media_label, 1, 0, 1, 6)

        self.widget.setLayout(layout)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.filter()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_start(self, index: int):
        """Updates the started attribute of the Media
        at the specified index

        :param index: The index of the Media to edit
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        started = self.widgets[index + 1][0].isChecked()
        finished = self.widgets[index + 1][1].isChecked()
        if started and finished:
            self.widgets[index + 1][1].setChecked(False)
        media_objects.get_media()[index].set_started(started)
        media_objects.get_media()[index].save()
        self.filter()

    def update_finish(self, index: int):
        """Updates the finished attribute of the Media
        at the specified index

        :param index: The index of the Media to edit
        """

        # Add 1 to the index when accessing the widgets
        #   due to the column headings
        finished = self.widgets[index + 1][1].isChecked()
        started = self.widgets[index + 1][0].isChecked()
        if finished and started:
            self.widgets[index + 1][0].setChecked(False)
        media_objects.get_media()[index].set_finished(finished)
        media_objects.get_media()[index].save()
        self.filter()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def filter(self):
        """Filters the Media in the ScrollArea"""
        filtered_media = media_objects.get_filtered_media()

        # Set the visibility of the widgets
        #   based off the filtered media
        for i in range(len(media_objects.get_media())):
            for mw in self.widgets[i + 1]:
                mw.setVisible(media_objects.get_media()[i] in filtered_media)
        self.no_media_label.setVisible(len(filtered_media) == 0)
