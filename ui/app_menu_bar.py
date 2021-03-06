import os
from functools import partial
from PyQt5 import QtWidgets

from ui import media_objects, MessageBox
from ui import ProviderDialog, PersonDialog
from util import csv_to_media, media_to_json, media_to_csv


class AppMenuBar(QtWidgets.QMenuBar):
    """The App Menu Bar consists of menu items and options
    to import and export media as a file

    :param update_media_func: The function used to update the media in the app
    """

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, update_media_func: callable = None,
                 update_providers_func: callable = None,
                 update_persons_func: callable = None):
        super().__init__(parent)
        self.update_media_func = update_media_func
        self.update_providers_func = update_providers_func
        self.update_persons_func = update_persons_func

        file_menu = self.addMenu("File")
        file_menu.addAction(" Import Media", self.import_media, "Ctrl+O")
        file_menu.addAction(" Export Media as JSON", partial(self.export_media, "json"), "Ctrl+E")
        file_menu.addAction(" Export Media as CSV", partial(self.export_media, "csv"), "Ctrl+Alt+E")

        options_menu = self.addMenu("Options")
        options_menu.addAction(" Configure Streaming Providers", self.configure_providers, "Ctrl+1")
        options_menu.addAction(" Configure Persons", self.configure_persons, "Ctrl+2")

        help_menu = self.addMenu("Help")
        help_menu.addAction(" Report Bug", lambda: print("report bug!"))

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def import_media(self):
        """Asks the user to select a file to import.
        The user will only be able to select either .json or .csv files
        """
        try:
            filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
                None, "Select Media", ".",
                "CSV Files(*.csv);;JSON Files(*.json)")
            media = []
            for filename in filenames:
                for media_obj in csv_to_media(filename):
                    media.append(media_obj)
                    media_obj.save()
            media_objects.get_media().extend(media)
            self.update_media_func()
            MessageBox("Import Success",
                       "Successfully imported media from the selected file(s)")
        except Exception as e:
            e = str(e)
            MessageBox("Import Failure",
                       f"The import failed because: \"{e}\"")

    def export_media(self, as_file: str):
        """Exports all Media into the specified filetype

        :param as_file: The file type to export the media as
        """
        if not os.path.exists("exports"):
            os.mkdir("exports")
        try:
            if as_file == "json":
                media_to_json(media_objects.get_media())
            if as_file == "csv":
                media_to_csv(media_objects.get_media())
            MessageBox("Export Success",
                       f"Successfully exported all media as {as_file}")
        except Exception as e:
            e = str(e)
            MessageBox("Export Failure",
                       f"The export failed because: \"{e}\"")

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def configure_providers(self):
        """Allows a user to configure the Streaming Providers in the application"""
        ProviderDialog(self, update_func=self.update_providers_func).exec_()

    def configure_persons(self):
        """Allows a user to configure the Persons in the application"""
        PersonDialog(self, update_func=self.update_persons_func).exec_()
