import os
import sys
from functools import partial

from PyQt5 import QtWidgets, QtCore

from media import Movie, TVShow, Podcast, LimitedSeries
from media.util import get_type
from ui import MovieDialog, MediaListWidget, add_grid_to_layout, media_objects
from ui import MessageBox
from options import options


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

    def __init__(self, views: dict, parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.views = views

        # Load all the media inside the movies, tv shows, podcasts, and limited series folders
        media = []
        paths = [Movie.FOLDER, TVShow.FOLDER, Podcast.FOLDER, LimitedSeries.FOLDER]
        for path in paths:
            if os.path.exists(f"{options.get_base_dir()}/data/{path}"):
                for file in os.listdir(f"{options.get_base_dir()}/data/{path}"):
                    try:
                        if path == Movie.FOLDER and file.endswith(".json"):
                            media.append(Movie(filename=f"{options.get_base_dir()}/data/{path}/{file}"))
                        elif path == TVShow.FOLDER and file.endswith(".json"):
                            media.append(TVShow(filename=f"{options.get_base_dir()}/data/{path}/{file}"))
                        elif path == Podcast.FOLDER and file.endswith(".json"):
                            media.append(Podcast(filename=f"{options.get_base_dir()}/data/{path}/{file}"))
                        elif path == LimitedSeries.FOLDER and file.endswith(".json"):
                            media.append(LimitedSeries(filename=f"{options.get_base_dir()}/data/{path}/{file}"))
                    except Exception as e:
                        MessageBox(f"Error loading {file}",
                                   str(e),
                                   self)
        media_objects.set_media(media)

        # Setup the MediaListWidget and the attributes for the filter comboboxes
        self.media_list_widget = MediaListWidget(
            self,
            edit_media_func=self.add_edit_media,
            remove_media_func=self.remove_media
        )

        self.filter_start_finish_combobox = None
        self.filter_type_combobox = None
        self.filter_provider_combobox = None
        self.filter_person_combobox = None
        self.clear_filter_button = None
        self.search_line_edit = None

        self.sort_type_button = None
        self.sort_provider_button = None
        self.sort_person_button = None
        self.sort_runtime_button = None
        self.sort_name_button = None
        self.clear_sort_button = None

        self.add_limited_series_button = None
        self.add_movie_button = None
        self.add_tv_show_button = None
        self.add_podcast_button = None

        self.setup_ui()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def setup_ui(self):
        """Combines all the necessary UI for the Home screen"""

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.setup_filters_ui(self))
        layout.addWidget(self.setup_sort_ui(self))
        layout.addWidget(self.media_list_widget, 1)
        layout.addWidget(self.setup_new_buttons_ui())

        self.setLayout(layout)
        self.show()

    def setup_filters_ui(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """Creates and returns a grid of widgets necessary for
        the filter widgets

        :param parent: The parent widget for the filter widgets
        """

        filters_widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QGridLayout()

        self.filter_start_finish_combobox = QtWidgets.QComboBox(parent)
        self.filter_start_finish_combobox.addItems(["All", "Started", "Finished",
                                                    "Not Started", "Not Finished", "Neither"])
        self.filter_start_finish_combobox.currentIndexChanged.connect(partial(self.filter_media, False))
        self.filter_start_finish_combobox.setToolTip("Filter the media by their started and finished status")

        self.filter_type_combobox = QtWidgets.QComboBox(parent)
        self.filter_type_combobox.addItems(["All"] + get_type())
        self.filter_type_combobox.currentIndexChanged.connect(partial(self.filter_media, False))
        self.filter_type_combobox.setToolTip("Filter the media by their type")

        self.filter_provider_combobox = QtWidgets.QComboBox(parent)
        self.filter_provider_combobox.addItems(["All"] + [provider for provider in options.get_providers()])
        self.filter_provider_combobox.currentIndexChanged.connect(partial(self.filter_media, False))
        self.filter_provider_combobox.setToolTip("Filter the media by the streaming provider")

        self.filter_person_combobox = QtWidgets.QComboBox(parent)
        self.filter_person_combobox.addItems(["All"] + [person for person in options.get_persons()])
        self.filter_person_combobox.currentIndexChanged.connect(partial(self.filter_media, False))
        self.filter_person_combobox.setToolTip("Filter the media by who is watching")

        self.clear_filter_button = QtWidgets.QPushButton("Clear Filter", parent)
        self.clear_filter_button.clicked.connect(partial(self.filter_media, True))
        self.clear_filter_button.setToolTip("Clear all media filters")

        self.search_line_edit = QtWidgets.QLineEdit(parent)
        self.search_line_edit.setPlaceholderText("Search")
        self.search_line_edit.textChanged.connect(partial(self.filter_media, False))
        self.search_line_edit.setToolTip("Search for specific media in the media queue")

        # Create the filter labels
        filter_labels = [
            QtWidgets.QLabel("Filter By Started/Finished"), None,
            QtWidgets.QLabel("Filter By Type"),
            QtWidgets.QLabel("Filter By Streaming Provider"),
            QtWidgets.QLabel("Filter By Person"),
            self.search_line_edit
        ]
        for label in filter_labels:
            if label is not None:
                label.setAlignment(QtCore.Qt.AlignHCenter)

        widgets = [filter_labels,
                   [self.filter_start_finish_combobox, None,
                    self.filter_type_combobox, self.filter_provider_combobox,
                    self.filter_person_combobox, self.clear_filter_button, None, None]]

        add_grid_to_layout(widgets, layout)
        filters_widget.setLayout(layout)
        return filters_widget

    def setup_sort_ui(self, parent: QtWidgets.QWidget) -> QtWidgets.QWidget:
        """Creates and returns a grid of widgets necessary for
        the sorting widgets

        :param parent: The parent widget for the filter widgets
        """

        sort_widgets = QtWidgets.QWidget(parent)
        layout = QtWidgets.QGridLayout()

        self.sort_type_button = QtWidgets.QPushButton("Sort By Type", parent)
        self.sort_type_button.clicked.connect(partial(self.cycle_sort, "type"))
        self.sort_type_button.setToolTip("Sort the Media by the Type")

        self.sort_provider_button = QtWidgets.QPushButton("Sort By Streaming Provider", parent)
        self.sort_provider_button.clicked.connect(partial(self.cycle_sort, "provider"))
        self.sort_provider_button.setToolTip("Sort the Media by the Streaming Provider")

        self.sort_person_button = QtWidgets.QPushButton("Sort By Person", parent)
        self.sort_person_button.clicked.connect(partial(self.cycle_sort, "person"))
        self.sort_person_button.setToolTip("Sort the Media by the Person")

        self.sort_runtime_button = QtWidgets.QPushButton("Sort By Runtime", parent)
        self.sort_runtime_button.clicked.connect(partial(self.cycle_sort, "runtime"))
        self.sort_runtime_button.setToolTip("Sort the Media by the Runtime")

        self.sort_name_button = QtWidgets.QPushButton("Sort By Name", parent)
        self.sort_name_button.clicked.connect(partial(self.cycle_sort, "name"))
        self.sort_name_button.setToolTip("Sort the Media by the Name")

        self.clear_sort_button = QtWidgets.QPushButton("Clear Sorting", parent)
        self.clear_sort_button.clicked.connect(partial(self.sort_media, True))
        self.clear_sort_button.setToolTip("Clear the sorting on the Media to the default")

        widgets = [[None, self.sort_type_button, self.sort_provider_button, self.sort_person_button,
                    self.sort_runtime_button, self.sort_name_button, self.clear_sort_button]]

        add_grid_to_layout(widgets, layout)
        sort_widgets.setLayout(layout)
        return sort_widgets

    def setup_new_buttons_ui(self):
        """Creates the buttons meant to be used when adding a new piece of Media"""

        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QGridLayout()

        self.add_movie_button = QtWidgets.QPushButton("Add Movie", self)
        self.add_movie_button.clicked.connect(partial(self.add_edit_media, 'Movie', None))
        self.add_movie_button.setToolTip("Add a new Movie to the media queue")

        self.add_tv_show_button = QtWidgets.QPushButton("Add TV Show", self)
        self.add_tv_show_button.clicked.connect(partial(self.add_edit_media, 'TV Show', None))
        self.add_tv_show_button.setToolTip("Add a new TV Show to the media queue")

        self.add_podcast_button = QtWidgets.QPushButton("Add Podcast", self)
        self.add_podcast_button.clicked.connect(partial(self.add_edit_media, 'Podcast', None))
        self.add_podcast_button.setToolTip("Add a new Podcast to the media queue")

        self.add_limited_series_button = QtWidgets.QPushButton("Add Limited Series", self)
        self.add_limited_series_button.clicked.connect(partial(self.add_edit_media, 'Limited Series', None))
        self.add_limited_series_button.setToolTip("Add a new Limited Series to the media queue")

        grid = [[self.add_movie_button, self.add_tv_show_button,
                 self.add_podcast_button, self.add_limited_series_button]]

        add_grid_to_layout(grid, layout)

        widget.setLayout(layout)

        return widget

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
                + This also means it will show started and uninitiated Media \n
            6.) Neither: This will show Media that has not been started nor finished

        :param clear: Whether or not to clear the filters
        """

        filter_start_finish = [None, None]
        filter_type = None
        filter_provider = None
        filter_person = None
        filter_search = None
        if clear:
            self.filter_start_finish_combobox.setCurrentIndex(0)
            self.filter_type_combobox.setCurrentIndex(0)
            self.filter_provider_combobox.setCurrentIndex(0)
            self.filter_person_combobox.setCurrentIndex(0)
            self.search_line_edit.setText("")
        else:

            # Get the filtering of the Started and Finished attributes
            filter_start_finish = (self.filter_start_finish_combobox.currentIndex()
                                   if self.filter_start_finish_combobox is not None else 0)
            filter_start_finish = {0: [None, None], 1: [True, False], 2: [False, True],
                                   3: [False, None], 4: [None, False], 5: [False, False]}[filter_start_finish]

            # Get the filtering of the Type of Media
            filter_type = (self.filter_type_combobox.currentText()
                           if self.filter_type_combobox is not None else "All")
            filter_type = filter_type if filter_type != "All" else None

            # Get the filtering of the Streaming Provider attribute
            filter_provider = (self.filter_provider_combobox.currentText()
                               if self.filter_provider_combobox is not None else "All")
            filter_provider = None if filter_provider == "All" else filter_provider

            # Get the filtering of the Person attribute
            filter_person = (self.filter_person_combobox.currentText()
                             if self.filter_person_combobox is not None else "All")
            filter_person = None if filter_person == "All" else filter_person

            # Get the filtering from the search bar
            filter_search = self.search_line_edit.text().lower()
            if len(filter_search) == 0:
                filter_search = None

        media_objects.set_media_filters(
            started=filter_start_finish[0], finished=filter_start_finish[1],
            media_type=filter_type, provider=filter_provider,
            person=filter_person, search=filter_search)
        self.media_list_widget.update_stats()
        self.media_list_widget.scroll_area.filter()

    def cycle_sort(self, sort: str):
        """Cycles the specified sorting variable to the next sort value

        :param sort: The sorting variable to cycle
        """

        # Cycle the correct sort
        if sort == "type":
            media_objects.cycle_type_sort()
            self.sort_type_button.setText("Sort By Type {}".format(
                "▲" if media_objects.get_type_sort() else
                ("▼" if media_objects.get_type_sort() is False else "")))
        elif sort == "provider":
            media_objects.cycle_provider_sort()
            self.sort_provider_button.setText("Sort By Streaming Provider {}".format(
                "▲" if media_objects.get_provider_sort() else
                ("▼" if media_objects.get_provider_sort() is False else "")))
        elif sort == "person":
            media_objects.cycle_person_sort()
            self.sort_person_button.setText("Sort By Person {}".format(
                "▲" if media_objects.get_person_sort() else
                ("▼" if media_objects.get_person_sort() is False else "")))
        elif sort == "runtime":
            media_objects.cycle_runtime_sort()
            self.sort_runtime_button.setText("Sort By Runtime {}".format(
                "▲" if media_objects.get_runtime_sort() else
                ("▼" if media_objects.get_runtime_sort() is False else "")))
        elif sort == "name":
            media_objects.cycle_name_sort()
            self.sort_name_button.setText("Sort By Name {}".format(
                "▲" if media_objects.get_name_sort() else
                ("▼" if media_objects.get_name_sort() is False else "")))

        self.sort_media()

    def sort_media(self, clear: bool = False):
        """Sorts the Media in the app based off the sorting values

        :param clear: Whether or not to set the sorting values to their defaults
        """
        if clear:
            media_objects.set_media_sort()
            self.sort_type_button.setText("Sort By Type")
            self.sort_provider_button.setText("Sort By Streaming Provider")
            self.sort_person_button.setText("Sort By Person")
            self.sort_runtime_button.setText("Sort By Runtime")
            self.sort_name_button.setText("Sort By Name")

        self.media_list_widget.scroll_area.update_ui()
        self.media_list_widget.scroll_area.filter()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def remove_media(self, index: int = None):
        """Removes the Media at the specified index from the list

        :param index: The index of the Media to remove
        """

        if index is not None:
            media_objects.get_removed_media().append(index)
            self.filter_media()

            media = media_objects.get_media()[index]
            os.remove(f"{options.get_base_dir()}/data/{media.FOLDER}/{media.get_id()}.json")

    def callback_tv_show(self, index: int = None, canceled: bool = False):
        """The callback function when a user is finished editing a TV Show

        :param index: The index of the TV Show to edit, if any.
        :param canceled: Whether or not the editing of a TV Show was canceled
        """

        self.parent().setCurrentWidget(self)
        self.window().setWindowTitle("Media Queue")

        # Get the TV Show object from the media objects
        tv_show = media_objects.get_tv_show()
        media_objects.set_tv_show()
        media_objects.set_episodes()
        if tv_show is not None:

            # Check if an index was given,
            #   modify the existing TV Show at the index given
            #   and update the widgets in the scroll area for the media list
            if index is not None:
                media_objects.get_media()[index] = tv_show
                hours, minutes = divmod(tv_show.get_runtime(), 60)
                self.media_list_widget.scroll_area.widgets[index + 1][0].setChecked(tv_show.is_started())
                self.media_list_widget.scroll_area.widgets[index + 1][1].setChecked(tv_show.is_finished())

                self.media_list_widget.scroll_area.widgets[index + 1][3].setText(tv_show.get_provider())
                self.media_list_widget.scroll_area.widgets[index + 1][4].setText(tv_show.get_person())
                self.media_list_widget.scroll_area.widgets[index + 1][5].setText("{}hr{} {}min{}".format(
                    hours, "s" if hours != 1 else "",
                    minutes, "s" if minutes != 1 else ""
                ))
                self.media_list_widget.scroll_area.widgets[index + 1][6].setText(tv_show.get_name())

            # No index was given, add the TV Show if the addition was not canceled
            #   then sort the media
            else:
                if not canceled:
                    media_objects.get_media().append(tv_show)
                media_objects.sort_media()

            # Update the UI for the scroll area and re-filter it
            self.media_list_widget.scroll_area.update_ui()
            self.filter_media()

    def callback_podcast(self, index: int = None, canceled: bool = False):
        """The callback function when a user is finished editing a Podcast

        :param index: The index of the Podcast to edit, if any.
        :param canceled: Whether or not the editing of a Podcast was canceled
        """

        self.parent().setCurrentWidget(self)
        self.window().setWindowTitle("Media Queue")

        # Get the Podcast object from the media objects
        podcast = media_objects.get_podcast()
        media_objects.set_podcast()
        media_objects.set_episodes()
        if podcast is not None:

            # Check if an index was given,
            #   modify the existing Podcast at the index given
            #   and update the widgets in the scroll area for the media list
            if index is not None:
                media_objects.get_media()[index] = podcast
                hours, minutes = divmod(podcast.get_runtime(), 60)
                self.media_list_widget.scroll_area.widgets[index + 1][0].setChecked(podcast.is_started())
                self.media_list_widget.scroll_area.widgets[index + 1][1].setChecked(podcast.is_finished())

                self.media_list_widget.scroll_area.widgets[index + 1][3].setText(podcast.get_provider())
                self.media_list_widget.scroll_area.widgets[index + 1][4].setText(podcast.get_person())
                self.media_list_widget.scroll_area.widgets[index + 1][5].setText("{}hr{} {}min{}".format(
                    hours, "s" if hours != 1 else "",
                    minutes, "s" if minutes != 1 else ""
                ))
                self.media_list_widget.scroll_area.widgets[index + 1][6].setText(podcast.get_name())
            else:

                # No index was given, add the Podcast if the addition was not canceled
                #   then sort the media
                if not canceled:
                    media_objects.get_media().append(podcast)
                media_objects.sort_media()

            # Update the UI for the scroll area and re-filter it
            self.media_list_widget.scroll_area.update_ui()
            self.filter_media()

    def callback_limited_series(self, index: int = None, canceled: bool = False):
        """The callback function when a user is finished editing a LimitedSeries

        :param index: The index of the LimitedSeries to edit, if any.
        :param canceled: Whether or not the editing of a LimitedSeries was canceled
        """

        self.parent().setCurrentWidget(self)
        self.window().setWindowTitle("Media Queue")

        # Get the Limited Series object from the media objects
        limited_series = media_objects.get_limited_series()
        media_objects.set_limited_series()
        media_objects.set_episodes()
        if limited_series is not None:

            # Check if an index was given,
            #   modify the existing Limited Series at the index given
            #   and update the widgets in the scroll area for the media list
            if index is not None:
                media_objects.get_media()[index] = limited_series
                hours, minutes = divmod(limited_series.get_runtime(), 60)
                self.media_list_widget.scroll_area.widgets[index + 1][0].setChecked(limited_series.is_started())
                self.media_list_widget.scroll_area.widgets[index + 1][1].setChecked(limited_series.is_finished())

                self.media_list_widget.scroll_area.widgets[index + 1][3].setText(limited_series.get_provider())
                self.media_list_widget.scroll_area.widgets[index + 1][4].setText(limited_series.get_person())
                self.media_list_widget.scroll_area.widgets[index + 1][5].setText("{}hr{} {}min{}".format(
                    hours, "s" if hours != 1 else "",
                    minutes, "s" if minutes != 1 else ""
                ))
                self.media_list_widget.scroll_area.widgets[index + 1][6].setText(limited_series.get_name())
            else:

                # No index was given, add the Limited Series if the addition was not canceled
                #   then sort the media
                if not canceled:
                    media_objects.get_media().append(limited_series)
                media_objects.sort_media()

            # Update the UI for the scroll area and re-filter it
            self.media_list_widget.scroll_area.update_ui()
            self.filter_media()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def add_edit_media(self, media_type: str, index: int = None):
        """Manages adding or editing a piece of Media with an optional index
        which controls whether or not a new piece of Media is being added

        :param media_type: The type of Media that is being added or edited
        :param index: The index of the Media to edit, if any.
        """

        # Set the proper media object in the media_objects class
        if index is not None:
            if media_type == "Movie":
                media_objects.set_movie(media_objects.get_media()[index])
            elif media_type == "Limited Series":
                media_objects.set_limited_series(media_objects.get_media()[index])
            elif media_type == "Podcast":
                media_objects.set_podcast(media_objects.get_media()[index])
            elif media_type == "TV Show":
                media_objects.set_tv_show(media_objects.get_media()[index])

        # Retrieve the next view and the callback function that will be used
        #   after adding/editing a piece of Media
        view_id = callback_func = None
        if media_type == "Movie":   # The Movie type is a dialog and therefore does not have a view
            movie_dialog = MovieDialog(self)
            if movie_dialog.result == QtWidgets.QDialog.Accepted:
                movie = media_objects.get_movie()
                media_objects.set_movie()
                if index is not None:
                    media_objects.get_media()[index] = movie
                else:
                    media_objects.get_media().append(movie)
                self.media_list_widget.scroll_area.update_ui()
                self.filter_media()

        # The Limited Series, Podcast, and TV Shows are other views which is
        #   why it's changed
        elif media_type == "Limited Series":
            view_id = "limited_series"
            callback_func = self.callback_limited_series
        elif media_type == "Podcast":
            view_id = "podcast"
            callback_func = self.callback_podcast
        elif media_type == "TV Show":
            view_id = "tv_show"
            callback_func = self.callback_tv_show

        if media_type != "Movie":
            self.views[view_id].edit(callback_func, index)
            self.parent().setCurrentWidget(self.views[view_id])

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_providers_filters(self):
        """Updates the list of providers in the combobox for providers filters"""
        self.filter_provider_combobox.clear()
        self.filter_provider_combobox.addItems(["All"] + [provider for provider in options.get_providers()])

    def update_persons_filters(self):
        """Updates the list of persons in the combobox for persons filters"""
        self.filter_person_combobox.clear()
        self.filter_person_combobox.addItems(["All"] + [person for person in options.get_persons()])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    home = Home({})
    sys.exit(app.exec_())
