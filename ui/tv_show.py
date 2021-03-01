import sys
from functools import partial
from typing import List

from PyQt5 import QtWidgets, QtCore

from media import StreamingProvider, Person, Season, TVShow
from ui import MessageBox, add_grid_to_layout


class TVShowView(QtWidgets.QFrame):
    def __init__(self, views: dict,
                 parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.views = views
        self.callback = None
        self.index = None

        self.seasons = []  # Keep track of the seasons and the created TV Show
        self.removed_seasons = []
        self.tv_show = None

        self.seasons_scroll_area = None
        self.seasons_widgets = None
        self.seasons_widget = None
        self.no_seasons_label = QtWidgets.QLabel("No Seasons", self)
        self.no_seasons_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.start_checkbox = None
        self.finish_checkbox = None
        self.add_season_button = None

        self.name_line_edit = None
        self.provider_dropdown = None
        self.person_dropdown = None
        self.person_dropdown = None

        self.cancel_button = None
        self.add_button = None
        self.save_button = None

        self.setup_ui()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def setup_ui(self):

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.setup_tv_show_ui(self))
        layout.addWidget(self.setup_seasons_ui())
        layout.addWidget(self.setup_finish_buttons_ui(self))

        self.setLayout(layout)
        self.show()

    def setup_tv_show_ui(self, parent: QtWidgets.QWidget):

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
        seasons_label = QtWidgets.QLabel("Seasons", widget)
        seasons_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.add_season_button = QtWidgets.QPushButton("Add", widget)

        self.name_line_edit = QtWidgets.QLineEdit(widget)
        self.name_line_edit.setPlaceholderText("TV Show Name")
        self.provider_dropdown = QtWidgets.QComboBox(widget)
        self.provider_dropdown.addItems([provider.value for provider in StreamingProvider])
        self.person_dropdown = QtWidgets.QComboBox(widget)
        self.person_dropdown.addItems([person.value for person in Person])

        grid = [[name_label, self.name_line_edit, None],
                [provider_label, self.provider_dropdown, None],
                [person_label, self.person_dropdown, None],
                [self.start_checkbox, self.finish_checkbox],
                [divider, None, None],
                [seasons_label, None, self.add_season_button]]

        add_grid_to_layout(grid, layout)

        widget.setLayout(layout)

        return widget

    def setup_seasons_ui(self):

        self.seasons_scroll_area = QtWidgets.QScrollArea(self)
        self.seasons_widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()

        add_grid_to_layout(self.setup_seasons_widgets(self.seasons_widget), layout)
        self.no_seasons_label.setParent(self.seasons_widget)
        layout.addWidget(self.no_seasons_label, 0, 0, 1, 2)

        self.seasons_widget.setLayout(layout)

        self.seasons_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.seasons_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.seasons_scroll_area.setAlignment(QtCore.Qt.AlignTop)
        self.seasons_scroll_area.setWidget(self.seasons_widget)

        return self.seasons_scroll_area

    def setup_finish_buttons_ui(self, parent: QtWidgets.QWidget):

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

    def setup_seasons_widgets(self, parent: QtWidgets.QWidget):
        """Creates the widgets for each Season

        This will return a list of lists where each sublist contains
        a widget that matches that of an actual Season object
        """

        widgets = []
        for i in range(len(self.seasons)):
            season = self.seasons[i]
            season_button = QtWidgets.QPushButton(season.get_season(), parent)
            season_button.clicked.connect(partial(self.add_edit_season, i))

            runtime_label = QtWidgets.QLabel("{} hour{}".format(
                season.get_runtime(True),
                "s" if season.get_runtime(True) != 1 else ""
            ), parent)

            remove_button = QtWidgets.QPushButton("Remove", parent)
            remove_button.clicked.connect(partial(self.remove_season, i))

            season_widgets = [season_button, runtime_label, remove_button]
            widgets.append(season_widgets)

        return widgets

    def update_seasons(self):
        self.seasons_scroll_area.widget().deleteLater()
        self.seasons_widgets = self.setup_seasons_widgets()
        self.seasons_scroll_area.setWidget(self.seasons_widgets)

        self.no_seasons_label.setVisible(len(self.seasons) == 0)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def callback_season(self, index: int = None, season: Season = None):
        self.parent().setCurrentWidget(self)

        if season is not None:
            if index is not None:
                self.seasons[index] = season
                self.season_widgets[index][0].setText(f"Season {season.get_season()}")
            else:
                self.seasons.append(season)
                self.update_seasons()

    def remove_season(self, index: int = None):
        pass

    def add_edit_season(self, index: int = None):
        season = None
        if index is not None:
            season = self.seasons[index]
        self.views["season"].edit(season, self.callback_season, index)
        self.parent().setCurrentWidget(self.views["season"])

    def cancel(self):
        """Resets the values for each widget and returns to the previous widget"""
        self.name_line_edit.setText("")
        self.provider_dropdown.setCurrentIndex(0)
        self.person_dropdown.setCurrentIndex(0)
        self.seasons = []
        self.callback()

    def add(self, is_saving: bool = False):
        """Saves the current TV Show as an object and loads it into the
        Media Queue app
        """
        try:
            if is_saving:
                id = self.tv_show.get_id()
            self.tv_show = TVShow(
                self.name_line_edit.text(),
                self.provider_dropdown.currentText(),
                self.person_dropdown.currentText(),
                self.seasons
            )
            if is_saving:
                self.tv_show.set_id(id)
            self.tv_show.save()
            self.callback(self.index, self.tv_show)
        except ValueError:
            MessageBox(
                "Missing Values",
                "You must specify the Name, the Streaming Provider and the Person")

    def edit(self, tv_show: TVShow, callback: callable, index: int):
        """Sets whether the user is editing or adding a TV Show in this view

        :param tv_show: The TV Show the user is editing, if any
        :param callback: The callback function when the user is done editing
        :param index: The index of the TV Show in the media list
        """
        self.tv_show = tv_show
        self.callback = callback
        self.index = index

        self.add_button.setVisible(tv_show is None)
        self.save_button.setVisible(tv_show is not None)

        if tv_show is not None:
            self.setWindowTitle(f"Edit {tv_show.get_name()}")
            self.name_line_edit.setText(tv_show.get_name())
            self.provider_dropdown.setCurrentText(tv_show.get_provider().value)
            self.person_dropdown.setCurrentText(tv_show.get_person().value)
        else:
            self.window().setWindowTitle("Add TV Show")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = TVShowView({})
    sys.exit(app.exec_())
