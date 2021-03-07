import sys
from PyQt5 import QtWidgets

from ui import Home, TVShowView, PodcastView, LimitedSeriesView
from ui import AppMenuBar


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
        self.limited_series_view = LimitedSeriesView(self.widget)
        self.podcast_view = PodcastView(self.widget)
        self.tv_show_view = TVShowView(self.widget)
        self.home_view = Home({
            "tv_show": self.tv_show_view,
            "podcast": self.podcast_view,
            "limited_series": self.limited_series_view
        }, self.widget)

        # Setup the Menu Bar for loading data into the Media Queue
        self.window.setMenuBar(AppMenuBar(self.widget,
                                          update_media_func=self.update_media,
                                          update_providers_func=self.update_providers,
                                          update_persons_func=self.update_persons))

        self.widget.addWidget(self.home_view)
        self.widget.addWidget(self.tv_show_view)
        self.widget.addWidget(self.podcast_view)
        self.widget.addWidget(self.limited_series_view)

        self.window.setCentralWidget(self.widget)
        self.window.show()
        self.center()
        sys.exit(self.exec_())

    def center(self):
        """Center the window on the screen"""
        self.window.setGeometry(0, 0,
                                2 * MediaQueue.RESOLUTION.width() // 3,
                                2 * MediaQueue.RESOLUTION.height() // 3)
        qt_rect = self.widget.currentWidget().frameGeometry()
        qt_rect.moveCenter(MediaQueue.CENTER)
        self.window.move(qt_rect.topLeft())

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def update_media(self):
        """Updates the stats about the media along with the Scroll Area widget"""
        self.home_view.media_list_widget.scroll_area.update_ui()
        self.home_view.media_list_widget.update_stats()

    def update_providers(self):
        """Updates any dropdowns that contain the list of providers"""
        self.home_view.update_providers_filters()
        self.limited_series_view.update_providers()
        self.podcast_view.update_providers()
        self.tv_show_view.update_providers()

    def update_persons(self):
        """Updates any dropdowns that contain the list of persons"""
        self.home_view.update_persons_filters()
        self.limited_series_view.update_persons()
        self.podcast_view.update_persons()
        self.tv_show_view.update_persons()


if __name__ == "__main__":
    app = MediaQueue(sys.argv)
