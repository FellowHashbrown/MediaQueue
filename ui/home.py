import sys
import os
from functools import partial, cmp_to_key

from PyQt5 import QtWidgets, QtCore

from media import Person, StreamingProvider, Movie, TVShow, Podcast, LimitedSeries
from media.util import get_type
from ui import add_grid_to_layout


class Home(QtWidgets.QFrame):
    """The Home screen is what the user sees when first opening up the
    Media Queue application

    There are 4 filter combo boxes so the user can easily filter by:
     1.) Whether or not the user has started or finished some Media
      * Note that a piece of Media cannot be started and finished at the same time \n
     2.) The type of Media (LimitedSeries, Movie, Podcast, TVShow) \n
     3.) The Streaming Provider
      * As of now, there are explicit options inside an Enumerated type. This may change \n
     4.) The Person watching it

    All the Media will follow an explicit sorting algorithm which will
    sort the Media in the precedence of Type -> Streaming Provider -> Person -> Name
    """

    def __init__(self, views: dict,
                 parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.views = views

        # Load all the media inside the movies, tv shows, podcasts, and limited series folders
        self.media = []
        paths = [Movie.FOLDER, TVShow.FOLDER, Podcast.FOLDER, LimitedSeries.FOLDER]
        for path in paths:
            if os.path.exists(f"./{path}"):
                for file in os.listdir(f"./{path}"):
                    if path == Movie.FOLDER and file.endswith(".json"):
                        self.media.append(Movie(filename=f"./{path}/{file}"))
                    elif path == TVShow.FOLDER and file.endswith(".json"):
                        self.media.append(TVShow(filename=f"./{path}/{file}"))
                    elif path == Podcast.FOLDER and file.endswith(".json"):
                        self.media.append(Podcast(filename=f"./{path}/{file}"))
                    elif path == LimitedSeries.FOLDER and file.endswith(".json"):
                        self.media.append(LimitedSeries(filename=f"./{path}/{file}"))
        self.sort_media()

        self.media_scroll_area = None
        self.media_widgets = self.setup_media_widgets()
        self.filtered_media = []
        self.removed_media = []  # This is a list of indices that should be ignored when filtering
        self.no_media_label = QtWidgets.QLabel("No Media", self)
        self.no_media_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.filter_start_finish_combobox = None
        self.filter_type_combobox = None
        self.filter_provider_combobox = None
        self.filter_person_combobox = None
        self.clear_filter_button = None

        self.add_limited_series_button = None
        self.add_movie_button = None
        self.add_tv_show_button = None
        self.add_podcast_button = None

        self.setup_ui()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def setup_ui(self):
        """Combines all the necessary UI for the Home screen"""

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.setup_new_buttons_ui())
        self.media_scroll_area = self.setup_media_ui()
        layout.addWidget(self.media_scroll_area)

        self.setLayout(layout)
        self.show()

    def setup_filters_ui(self, widget) -> list:
        """Creates and returns a grid of widgets necessary for
        the filter widgets

        :param widget: The parent widget for the filter widgets
        """

        self.filter_start_finish_combobox = QtWidgets.QComboBox(widget)
        self.filter_start_finish_combobox.addItems(["All", "Started", "Finished",
                                                    "Not Started", "Not Finished", "Neither"])
        self.filter_start_finish_combobox.currentIndexChanged.connect(partial(self.filter_media, False))

        self.filter_type_combobox = QtWidgets.QComboBox(widget)
        self.filter_type_combobox.addItems(["All"] + get_type())
        self.filter_type_combobox.currentIndexChanged.connect(partial(self.filter_media, False))

        self.filter_provider_combobox = QtWidgets.QComboBox(widget)
        self.filter_provider_combobox.addItems(["All"] + [provider.value for provider in StreamingProvider])
        self.filter_provider_combobox.currentIndexChanged.connect(partial(self.filter_media, False))

        self.filter_person_combobox = QtWidgets.QComboBox(widget)
        self.filter_person_combobox.addItems(["All"] + [person.value for person in Person])
        self.filter_person_combobox.currentIndexChanged.connect(partial(self.filter_media, False))

        self.clear_filter_button = QtWidgets.QPushButton("Clear Filter", widget)
        self.clear_filter_button.clicked.connect(partial(self.filter_media, True))

        # Create the filter labels
        filter_labels = [QtWidgets.QLabel("Filter By") for _ in range(5)]
        for label in filter_labels:
            label.setAlignment(QtCore.Qt.AlignHCenter)
        # noinspection PyTypeChecker
        filter_labels[1] = None     # This removes the second label in order to give room
                                    # for the started and finished filters to be combined
                                    # into one filter

        return [filter_labels,
                [self.filter_start_finish_combobox, None,
                 self.filter_type_combobox, self.filter_provider_combobox,
                 self.filter_person_combobox, self.clear_filter_button, None]]

    def setup_media_ui(self):
        """Creates the scrolling area for the media widgets to exist in"""

        self.media_scroll_area = QtWidgets.QScrollArea(self)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()

        layout.setAlignment(QtCore.Qt.AlignTop)

        filters = self.setup_filters_ui(widget)
        add_grid_to_layout(filters, layout)
        add_grid_to_layout(self.media_widgets, layout, 2)
        layout.addWidget(self.no_media_label, 2, 0, 1, 7)
        self.filter_media()

        widget.setLayout(layout)

        self.media_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.media_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.media_scroll_area.setAlignment(QtCore.Qt.AlignTop)
        self.media_scroll_area.setWidget(widget)

        return self.media_scroll_area

    def setup_new_buttons_ui(self):
        """Creates the buttons meant to be used when adding a new piece of Media"""

        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QGridLayout()

        self.add_movie_button = QtWidgets.QPushButton("Add Movie", self)
        self.add_movie_button.clicked.connect(partial(self.add_edit_movie, None))

        self.add_tv_show_button = QtWidgets.QPushButton("Add TV Show", self)
        self.add_tv_show_button.clicked.connect(partial(self.add_edit_tv_show, None))

        self.add_podcast_button = QtWidgets.QPushButton("Add Podcast", self)
        self.add_podcast_button.clicked.connect(partial(self.add_edit_podcast, None))

        self.add_limited_series_button = QtWidgets.QPushButton("Add Limited Series", self)
        self.add_limited_series_button.clicked.connect(partial(self.add_edit_limited_series, None))

        grid = [[self.add_movie_button, self.add_tv_show_button,
                 self.add_podcast_button, self.add_limited_series_button]]

        add_grid_to_layout(grid, layout)

        widget.setLayout(layout)

        return widget

    def setup_media_widgets(self):
        """Creates the widgets for each piece of Media

        This will return a list of lists where each sublist contains
        a widget that matches that of an actual Media object
        """

        widgets = []
        for i in range(len(self.media)):
            media = self.media[i]
            start_checkbox = QtWidgets.QCheckBox("Started?", self)
            start_checkbox.setChecked(media.is_started())
            start_checkbox.clicked.connect(partial(self.update_start, i))

            finish_checkbox = QtWidgets.QCheckBox("Finished?", self)
            finish_checkbox.setChecked(media.is_finished())
            finish_checkbox.clicked.connect(partial(self.update_finish, i))

            type_label = QtWidgets.QLabel(get_type(media), self)
            provider_label = QtWidgets.QLabel(media.get_provider().value, self)
            person_label = QtWidgets.QLabel(media.get_person().value, self)

            runtime_text = "{} hour{}".format(
                media.get_runtime(True),
                "s" if media.get_runtime(True) != 1 else "")
            runtime_label = QtWidgets.QLabel(runtime_text, self)

            media_button = QtWidgets.QPushButton(media.get_name(), self)
            if isinstance(media, Movie):
                media_button.clicked.connect(
                    partial(self.add_edit_movie, i))
            elif isinstance(media, LimitedSeries):
                media_button.clicked.connect(
                    partial(self.add_edit_limited_series, i))
            elif isinstance(media, Podcast):
                media_button.clicked.connect(
                    partial(self.add_edit_podcast, i))
            elif isinstance(media, TVShow):
                media_button.clicked.connect(
                    partial(self.add_edit_tv_show, i))

            remove_button = QtWidgets.QPushButton("Remove", self)
            remove_button.clicked.connect(partial(self.remove_media, i))

            media_widgets = [start_checkbox, finish_checkbox,
                             type_label, provider_label, person_label,
                             runtime_label, media_button, remove_button]

            widgets.append(media_widgets)

        return widgets

    def update_media(self):
        """Updates the Media widgets in the app by removing the original
        scroll area from the layout, updating the widgets for each type of Media,
        and updating the scroll area while adding it back to the layout
        """

        self.parent().removeWidget(self.media_scroll_area)
        self.media_scroll_area.deleteLater()

        self.media_widgets = self.setup_media_widgets()

        self.media_scroll_area = self.setup_media_ui()
        self.parent().addWidget(self.media_scroll_area)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def filter_media(self, clear: bool = False):
        """Filters the Media in the app based off the filter combo boxes

        Because the start and finish attributes of a Media object
        cannot be True at the same time, the filter comes from a combination laid out below:
            1.) All: This will show all pieces of Media no matter their start and finish attributes \n
            2.) Started: This will show only the Media that has been started \n
            3.) Finished: This will show only the Media that has been finished \n
            4.) Not Started: This will show the Media that has not been started
                + This also means it will show finished and unfinished Media \n
            5.) Not Finished: This will show the Media that has not been finished
                + This also means it will show started and unstarted Media \n
            6.) Neither: This will show Media that has not been started nor finished

        :param clear: Whether or not to clear the filters
        """

        filter_start_finish = [None, None]
        filter_type = "All"
        filter_provider = None
        filter_person = None
        if clear:
            self.filter_start_finish_combobox.setCurrentIndex(0)
            self.filter_type_combobox.setCurrentIndex(0)
            self.filter_provider_combobox.setCurrentIndex(0)
            self.filter_person_combobox.setCurrentIndex(0)
        else:

            # Get the filtering of the Started and Finished attributes
            filter_start_finish = (self.filter_start_finish_combobox.currentIndex()
                                   if self.filter_start_finish_combobox is not None else 0)
            filter_start_finish = {0: [None, None], 1: [True, False], 2: [False, True],
                                   3: [False, None], 4: [None, False], 5: [False, False]}[filter_start_finish]

            # Get the filtering of the Type of Media
            filter_type = (self.filter_type_combobox.currentText()
                           if self.filter_type_combobox is not None else "All")
            filter_type = get_type(filter_type, True) if filter_type != "All" else "All"

            # Get the filtering of the Streaming Provider attribute
            filter_provider = (self.filter_provider_combobox.currentText()
                               if self.filter_provider_combobox is not None else "All")
            filter_provider = None if filter_provider == "All" else StreamingProvider(filter_provider)

            # Get the filtering of the Person attribute
            filter_person = (self.filter_person_combobox.currentText()
                             if self.filter_person_combobox is not None else "All")
            filter_person = None if filter_person == "All" else Person(filter_person)

        # Filter the Media
        self.filtered_media = []
        for i in range(len(self.media)):
            media = self.media[i]
            if i in self.removed_media:
                continue

            if filter_start_finish[0] is not None:
                if media.is_started() is not filter_start_finish[0]:
                    continue

            if filter_start_finish[1] is not None:
                if media.is_finished() is not filter_start_finish[1]:
                    continue

            if filter_type != "All":
                if type(media) != filter_type:
                    continue

            if filter_provider is not None:
                if media.get_provider() != filter_provider:
                    continue

            if filter_person is not None:
                if media.get_person() != filter_person:
                    continue

            self.filtered_media.append(media)

        # Show or Hide all the widgets associated with the Media
        #   that should be filtered
        for i in range(len(self.media)):
            for mw in self.media_widgets[i]:
                mw.setVisible(self.media[i] in self.filtered_media)
        self.no_media_label.setVisible(len(self.filtered_media) == 0)

    def sort_media(self):
        """Sorts the Media that exists in the order of
        Type -> Streaming Provider -> Person -> Name
        """

        def sort_key(a, b):
            """A local function meant to be used as a sorting key"""

            # Types are the same, move to Provider
            if get_type(a) == get_type(b):

                # Providers are the same, move to Person
                if a.get_provider().value == b.get_provider().value:

                    # Persons are the same, move to name
                    if a.get_person().value == b.get_person().value:

                        if a.get_name() == b.get_name():
                            return 0
                        elif a.get_name() < b.get_name():
                            return -1
                        return 1

                    # Persons are different
                    elif a.get_person().value < b.get_person().value:
                        return -1
                    return 1

                # Providers are different
                elif a.get_provider().value < b.get_provider().value:
                    return -1
                return 1

            # Types are different
            elif get_type(a) < get_type(b):
                return -1
            return 1

        self.media = sorted(self.media, key=cmp_to_key(sort_key))

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_start(self, index: int):
        """Updates the Media whenever the Started checkbox is clicked

        :param index: The index of the Media to update
        """
        start_check = self.media_widgets[index][0]
        finish_check = self.media_widgets[index][1]
        media = self.media[index]

        if start_check.isChecked() and media.is_finished():
            finish_check.setChecked(False)
        media.set_started(start_check.isChecked())
        media.save()
        self.filter_media()

    def update_finish(self, index: int):
        """Updates the Media whenever the Finished checkbox is clicked

        :param index: The index of the Media to update
        """
        start_check = self.media_widgets[index][0]
        finish_check = self.media_widgets[index][1]
        media = self.media[index]

        if finish_check.isChecked() and media.is_started():
            start_check.setChecked(False)
        media.set_finished(finish_check.isChecked())
        media.save()
        self.filter_media()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def remove_media(self, index: int = None):
        """Removes the Media at the specified index from the list

        :param index: The index of the Media to remove
        """

        if index is not None:
            self.removed_media.append(index)
            self.filter_media()

    def callback_movie(self, index: int = None, movie: Movie = None):
        """The callback function whenever the Movie is done being edited

        :param index: The index of the movie to edit the entry for, if any
        :param movie: The movie to add/edit
        """

        self.parent().setCurrentWidget(self)
        self.window().setWindowTitle("Media Queue")

        if movie is not None:

            # The result of editing a movie
            if index is not None:
                self.media[index] = movie
                self.media_widgets[index][0].setChecked(movie.is_started())
                self.media_widgets[index][1].setChecked(movie.is_finished())

                self.media_widgets[index][3].setText(movie.get_provider().value)
                self.media_widgets[index][4].setText(movie.get_person().value)
                self.media_widgets[index][5].setText(movie.get_name())

            # The result of adding a movie
            else:
                self.media.append(movie)
                self.sort_media()
                self.update_media()
            self.filter_media()

    def callback_tv_show(self, index: int = None, tv_show: TVShow = None):

        self.parent().setCurrentWidget(self)
        self.window().setWindowTitle("Media Queue")

        if tv_show is not None:

            if index is not None:
                pass
            else:
                self.media.append(tv_show)
                self.sort_media()
                self.update_media()
            self.filter_media()

    def callback_podcast(self, index: int = None, podcast: Podcast = None):
        pass

    def callback_limited_series(self, index: int = None, limited_series: LimitedSeries = None):
        pass

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def add_edit_movie(self, index: int = None):
        media = None
        if index is not None:
            media = self.media[index]
        self.views["movie"].edit(media, self.callback_movie, index)
        self.parent().setCurrentWidget(self.views["movie"])

    def add_edit_tv_show(self, index: int = None):
        media = None
        if index is not None:
            media = self.media[index]
        self.views["tv_show"].edit(media, self.callback_tv_show, index)
        self.parent().setCurrentWidget(self.views["tv_show"])

    def add_edit_podcast(self, index: int = None):
        pass

    def add_edit_limited_series(self, index: int = None):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    home = Home()
    sys.exit(app.exec_())
