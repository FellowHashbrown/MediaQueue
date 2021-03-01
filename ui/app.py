import sys
from functools import partial
from PyQt5 import QtWidgets

from ui import Home, MovieView, TVShowView


class MediaQueue(QtWidgets.QApplication):
    """The main Media Queue application"""

    RESOLUTION = None
    CENTER = None

    def __init__(self, *args):
        super().__init__(*args)
        MediaQueue.RESOLUTION = QtWidgets.QDesktopWidget().availableGeometry()
        MediaQueue.CENTER = QtWidgets.QDesktopWidget().availableGeometry().center()

        # Set up the Main Window
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle("Media Queue")

        # Set up the layout
        self.widget = QtWidgets.QStackedWidget(self.window)
        self.widget.currentChanged.connect(self.center)

        # Set up the views
        # episode_view = EpisodeView(widget)
        # season_view = SeasonView(layout, {"episode": episode_view}, widget)
        # limited_series_view = LimitedSeriesView(layout, {"episode": episode_view}, widget)
        # podcast_view = PodcastView(layout, {"season": season_view}, widget))
        tv_show_view = TVShowView({}, self.widget)
        movie_view = MovieView(self.widget)
        home_view = Home({
            "movie": movie_view,
            "tv_show": tv_show_view,
            # "podcast": podcast_view,
            # "limited_series_view": limited_series_view
        }, self.widget)

        self.widget.addWidget(home_view)
        self.widget.addWidget(movie_view)
        self.widget.addWidget(tv_show_view)
        # layout.addWidget(podcast_view)
        # layout.addWidget(limited_series_view)
        # layout.addWidget(season_view)
        # layout.addWidget(episode_view)

        self.window.setCentralWidget(self.widget)
        self.window.show()
        self.center()
        sys.exit(self.exec_())

    def center(self):
        qt_rect = self.widget.currentWidget().frameGeometry()
        qt_rect.moveCenter(MediaQueue.CENTER)
        self.window.move(qt_rect.topLeft())


if __name__ == "__main__":
    app = MediaQueue(sys.argv)
