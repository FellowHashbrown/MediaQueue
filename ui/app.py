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
        limited_series_view = LimitedSeriesView(self.widget)
        podcast_view = PodcastView(self.widget)
        tv_show_view = TVShowView(self.widget)
        home_view = Home({
            "tv_show": tv_show_view,
            "podcast": podcast_view,
            "limited_series": limited_series_view
        }, self.widget)

        # Setup the Menu Bar for loading data into the Media Queue
        self.window.setMenuBar(AppMenuBar(self.widget,
                                          update_media_func=home_view.media_list_widget.scroll_area.update_ui))

        self.widget.addWidget(home_view)
        self.widget.addWidget(tv_show_view)
        self.widget.addWidget(podcast_view)
        self.widget.addWidget(limited_series_view)

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


if __name__ == "__main__":
    app = MediaQueue(sys.argv)
