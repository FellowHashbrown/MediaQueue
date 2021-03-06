import os
from json import dump
from typing import List

from media import Season, Show


class TVShow(Show):
    """A TVShow consists of Season of Episodes.

    :param name: The name of this TVShow
    :param seasons: The Season in this TVShow
    :param provider: The name of the streaming provider this TVShow is located on
    :param person: The person that is watching this TVShow

    :keyword started: Whether or not this TVShow has been started (Defaults to False)
    :keyword finished: Whether or not this TVShow has been finished (Defaults to False)
    :keyword json: The JSON object to load a TVShow object from
    :keyword filename: The JSON file to load a TVShow object from

    :raises FileNotFoundError: When the JSON file cannot be found
    :raises KeyError: When the required parameters are missing from the JSON object
    """

    FOLDER = "tvShows"

    def __init__(self, name: str = None, provider: str = None,
                 person: str = None, seasons: List[Season] = None,
                 *, started: bool = False, finished: bool = False,
                 json: dict = None, filename: str = None):
        super().__init__(name, provider, person,
                         seasons=seasons,
                         started=started, finished=finished,
                         json=json, filename=filename)

    def __str__(self):
        return "TVShow({}, {}, {}, {}, {}, {}, {})".format(
            self.get_id(), self.get_name(),
            self.get_provider(), self.get_person(),
            "Started" if self.is_started() else "Not Started",
            "Finished" if self.is_finished() else "Not Finished",
            ", ".join([str(season) for season in self.get_seasons()])
        )

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

    def to_csv(self) -> str:
        """Returns the CSV representation of this TVShow object"""
        show_csv = "\"{}\",{},{},{},{}".format(
            self.get_name(),
            self.get_provider(), self.get_person(),
            self.is_started(), self.is_finished()
        )
        episodes_csv = "\n".join(
            episode.to_csv()
            for season in self.get_seasons()
            for episode in season.get_episodes()
        )
        return f"TVShow\n{show_csv}\n{episodes_csv}"

    def to_json(self) -> dict:
        """Returns the JSON representation of this TVShow object"""
        super_json = super().to_json()
        super_json.pop("episodes")  # A TV Show consists of Seasons of Episodes
        return super_json

    def save(self):
        """Saves this TVShow object into a JSON file"""
        if not os.path.exists(f"./data/{TVShow.FOLDER}"):
            os.mkdir(f"./data/{TVShow.FOLDER}")
        with open("./data/{}/{}.json".format(TVShow.FOLDER, self.get_id()), "w") as jsonfile:
            dump(self.to_json(), jsonfile, indent=4)
