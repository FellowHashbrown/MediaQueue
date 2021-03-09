from enum import Enum

from PyQt5 import QtWidgets, QtGui, QtCore


class HelpDialog(QtWidgets.QDialog):
    """The Help Dialog will show a screenshot of the specified image
    which comes from whichever Help action the user chooses
    """

    class HelpImage(Enum):
        """An enumerated class to identify the locations of certain
        screenshots for the Help menu
        """

        HOME = "help/screenshots/MQ_Home_annotated.png"
        TV_SHOW = "help/screenshots/MQ_TV_Show_annotated.png"
        PODCAST = "help/screenshots/MQ_Podcast_annotated.png"
        LIMITED_SERIES = "help/screenshots/MQ_Limited_Series_annotated.png"

    def __init__(self, image: HelpImage, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.image = image

        resolution = QtWidgets.QDesktopWidget().availableGeometry()
        image_label = QtWidgets.QLabel(self)
        image_pixmap = QtGui.QPixmap(image.value)
        image_pixmap = image_pixmap.scaledToWidth(4 * resolution.width() // 5)
        image_label.setPixmap(image_pixmap)
        self.resize(image_pixmap.width(), image_pixmap.height())
        self.show()
