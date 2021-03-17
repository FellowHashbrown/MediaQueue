import os
import webbrowser
from functools import partial

from PyQt5 import QtWidgets

from ui import media_objects, MessageBox
from ui import ProviderDialog, PersonDialog
from util import json_to_media, csv_to_media, media_to_json, media_to_csv
from options import options


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

        self.file_menu = self.addMenu("File")
        self.file_menu_import_all = self.file_menu.addMenu(" Import Media")
        self.file_menu_import_all.addAction(
            " From JSON", partial(self.import_media, "json"), "Ctrl+O")
        self.file_menu_import_all.addAction(
            " From CSV", partial(self.import_media, "csv"), "Ctrl+Shift+O")
        self.file_menu.addSeparator()

        self.file_menu_export_current = self.file_menu.addMenu(" Export Current Media")
        self.file_menu_export_current.addAction(" To JSON", partial(self.export_media, "json", True), "Ctrl+S")
        self.file_menu_export_current.addAction(" To CSV", partial(self.export_media, "csv", True), "Ctrl+Shift+S")

        self.file_menu_export_all = self.file_menu.addMenu(" Export All Media")
        self.file_menu_export_all.addAction(
            " To JSON", partial(self.export_media, "json", False), "Alt+S")
        self.file_menu_export_all.addAction(
            " To CSV", partial(self.export_media, "csv", False), "Alt+Shift+S")

        self.options_menu = self.addMenu("Options")
        self.options_menu.addAction(" Configure Streaming Providers", self.configure_providers, "Ctrl+1")
        self.options_menu.addAction(" Configure Persons", self.configure_persons, "Ctrl+2")

        def open_browser():
            webbrowser.open("https://github.com/FellowHashbrown/MediaQueue/blob/master/README.md")
        self.help_menu = self.addMenu("Help")
        self.help_menu.addAction(" How to Use", open_browser)
        self.help_menu.addAction(" Report Bug or Request Feature", self.show_report_bug)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def import_media(self, as_file: str):
        """Asks the user to select a file to import.
        The user will only be able to select .csv files
        """
        try:
            filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
                None, "Select Media", ".",
                "CSV Files(*.csv)" if as_file == "csv" else "JSON Files(*.json)")
            if len(filenames) > 0:
                if as_file == "csv":
                    target_load_func = csv_to_media
                else:
                    target_load_func = json_to_media
                media = []
                for filename in filenames:
                    for media_obj in target_load_func(filename):
                        media.append(media_obj)
                        media_obj.save()
                media_objects.get_media().extend(media)
                self.update_media_func()
                MessageBox("Import Success",
                           "Successfully imported media from the selected file(s)",
                           self)
        except Exception as e:
            e = str(e)
            MessageBox("Import Failure",
                       f"The import failed because: \"{e}\"",
                       self)

    def export_media(self, as_file: str, single: False):
        """Exports all Media into the specified filetype

        :param as_file: The file type to export the media as
        :param single: Whether or not to export a single piece of Media
        """
        if not os.path.exists(f"{options.get_base_dir()}/exports"):
            os.mkdir(f"{options.get_base_dir()}/exports")
        try:
            media = media_objects.get_media()
            if single:
                inner_media = None
                if media_objects.get_movie() is not None:
                    inner_media = media_objects.get_movie()
                elif media_objects.get_tv_show() is not None:
                    inner_media = media_objects.get_tv_show()
                elif media_objects.get_podcast() is not None:
                    inner_media = media_objects.get_podcast()
                elif media_objects.get_limited_series() is not None:
                    inner_media = media_objects.get_limited_series()

                # Check if the media is None
                if inner_media is None:
                    raise ValueError("There is no specific piece of Media open right now")
                media = inner_media

            # Export the media
            if as_file == "json":
                media_to_json(media)
            if as_file == "csv":
                media_to_csv(media)
            MessageBox("Export Success",
                       "Successfully exported {} as {}".format(
                           "all media" if not single else f"\"{media.get_name()}\"",
                           as_file),
                       self)
        except Exception as e:
            e = str(e)
            MessageBox("Export Failure",
                       f"The export failed because: \"{e}\"",
                       self)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def configure_providers(self):
        """Allows a user to configure the Streaming Providers in the application"""
        ProviderDialog(self, update_func=self.update_providers_func).exec_()

    def configure_persons(self):
        """Allows a user to configure the Persons in the application"""
        PersonDialog(self, update_func=self.update_persons_func).exec_()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def show_report_bug(self):
        """Shows the user a dialog on how to report a bug in Media Queue"""
        MessageBox("How to Report a Bug",
                   "In order to report a bug, I ask that you go here to do so",
                   self,
                   link_title="Github Bug Reporter",
                   link_url="https://github.com/FellowHashbrown/MediaQueue/issues/new/choose")
