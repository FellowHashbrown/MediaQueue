import os
from json import dump
from typing import List

from media import Season, TVShow
from options import options


class Podcast(TVShow):
    """A Podcast consists of Season of Episodes.

    :param name: The name of this Podcast
    :param seasons: The Season in this Podcast
    :param provider: The name of the streaming provider this Podcast is located on
    :param person: The person that is watching this Podcast

    :keyword started: Whether or not this Podcast has been started (Defaults to False)
    :keyword finished: Whether or not this Podcast has been finished (Defaults to False)
    :keyword json: The JSON object to load a Podcast object from
    :keyword filename: The JSON file to load a Podcast object from

    :raises FileNotFoundError: When the JSON file cannot be found
    :raises KeyError: When the required parameters are missing from the JSON object
    """

    FOLDER = "podcasts"

    def __init__(self, name: str = None, provider: str = None,
                 person: str = None, seasons: List[Season] = None,
                 *, started: bool = False, finished: bool = False,
                 json: dict = None, filename: str = None):
        super().__init__(name, provider, person, seasons,
                         started=started, finished=finished,
                         json=json, filename=filename)

    def __str__(self):
        return "Podcast({}, {}, {}, {}, {}, {}, {})".format(
            self.get_id(), self.get_name(),
            self.get_provider(), self.get_person(),
            "Started" if self.is_started() else "Not Started",
            "Finished" if self.is_finished() else "Not Finished",
            ", ".join([str(season) for season in self.get_seasons()])
        )

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def to_csv(self) -> str:
        """Returns the JSON representation of this Podcast"""
        return super().to_csv().replace("TVShow", "Podcast", 1)

    def save(self):
        """Saves this Podcast object into a JSON file"""
        if not os.path.exists(f"{options.get_base_dir()}/data"):
            os.mkdir(f"{options.get_base_dir()}/data")
        if not os.path.exists(f"{options.get_base_dir()}/data/{Podcast.FOLDER}"):
            os.mkdir(f"{options.get_base_dir()}/data/{Podcast.FOLDER}")
        with open("{}/data/{}/{}.json".format(options.get_base_dir(), Podcast.FOLDER, self.get_id()), "w") as jsonfile:
            dump(self.to_json(), jsonfile, indent=4)
