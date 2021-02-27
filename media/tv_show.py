import os
from json import dump
from typing import List, Union

from media import Person, StreamingProvider, Season, Show


class TVShow(Show):
    """A TVShow consists of Season of Episodes.

    :param name: The name of this TVShow
    :param seasons: The Season in this TVShow
    :param provider: The name of the StreamingProvider this TVShow is located on
    :param person: The Person that is watching this TVShow

    :keyword started: Whether or not this TVShow has been started (Defaults to False)
    :keyword finished: Whether or not this TVShow has been finished (Defaults to False)
    :keyword json: The JSON object to load a TVShow object from
    :keyword filename: The JSON file to load a TVShow object from

    :raises FileNotFoundError: When the JSON file cannot be found
    :raises KeyError: When the required parameters are missing from the JSON object
    """

    FOLDER = "tvShows"

    def __init__(self, name: str = None, provider: Union[StreamingProvider, str] = None,
                 person: Union[Person, str] = None, seasons: List[Season] = None,
                 *, started: bool = False, finished: bool = False,
                 json: dict = None, filename: str = None):
        super().__init__(name, provider, person,
                         seasons=seasons,
                         started=started, finished=finished,
                         json=json, filename=filename)

    def __eq__(self, tv_show: 'TVShow'):
        if not isinstance(tv_show, TVShow):
            return False
        return (tv_show.get_name() == self.get_name() and
                set(tv_show.get_seasons()) == set(self.get_seasons()) and
                tv_show.get_provider() == self.get_provider() and
                tv_show.get_person() == self.get_person() and
                tv_show.is_started() == self.is_started() and
                tv_show.is_finished() == self.is_finished())

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def to_json(self) -> dict:
        """Returns the JSON representation of this TVShow object"""
        super_json = super().to_json()
        super_json.pop("episodes")  # A TV Show consists of Seasons of Episodes
        return super_json

    def save(self):
        """Saves this TVShow object into a JSON file"""
        if not os.path.exists(TVShow.FOLDER):
            os.mkdir(TVShow.FOLDER)
        with open("./{}/{}.json".format(TVShow.FOLDER, self.get_id()), "w") as jsonfile:
            dump(self.to_json(), jsonfile, indent=4)
