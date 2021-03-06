import os
from json import dump, load
from typing import List, Union

from media import Media, Season, Episode


class Show(Media):
    """A Show can be anything like a regular TV Show, a Limited Series,
    or a Podcast

    Note that this should not be created. Use TVShow, LimitedSeries, or Podcast

    :param name: The name of this Show
    :param provider: The name of the StreamingProvider this Show is located on
    :param person: The Person that is watching this Show

    :keyword started: Whether or not this Show has been started (Defaults to False)
    :keyword finished: Whether or not this Show has been finished (Defaults to False)
    :keyword json: The JSON object to load a Show object from
    :keyword filename: The JSON file to load a Show object from

    :raises FileNotFoundError: When the JSON file cannot be found
    :raises KeyError: When the required parameters are missing from the JSON object
    """

    FOLDER = "shows"

    def __init__(self, name: str = None,
                 provider: str = None,
                 person: str = None,
                 *, seasons: List[Season] = None, episodes: List[Episode] = None,
                 started: bool = False, finished: bool = False,
                 json: dict = None, filename: str = None):
        super().__init__(name, provider, person,
                         started=started, finished=finished,
                         json=json, filename=filename)

        # Check if a JSON file was given
        if filename is not None:
            with open(filename, "r") as jsonfile:
                json = load(jsonfile)

        # Check if a JSON object was given
        if json is not None:
            if {"seasons", "episodes"}.isdisjoint(json.keys()):
                raise KeyError("Seasons or Episodes must be given")

            seasons = json.get("seasons", None)
            episodes = json.get("episodes", None)

            # Convert the Seasons/Episodes to objects
            if seasons is not None:
                seasons = [Season(json=season) for season in seasons]
            if episodes is not None:
                episodes = [Episode(json=episode) for episode in episodes]

        self.__seasons = seasons
        self.__episodes = episodes

    def __eq__(self, show: 'Show'):
        if not isinstance(show, Show):
            return False
        return (show.get_name() == self.get_name() and
                show.get_provider() == self.get_provider() and
                show.get_person() == self.get_person() and
                {show.get_seasons()} == {self.get_seasons()} and
                {show.get_episodes()} == {self.get_episodes()} and
                show.is_started() is self.is_started() and
                show.is_finished() is self.is_finished())

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_seasons(self) -> Union[List[Season], None]:
        """Returns the list of Seasons in this Show or None if no Seasons
        should exist (i.e. only Episodes exist)
        """
        if self.__seasons is not None:
            return [season for season in self.__seasons]
        return self.__seasons

    def get_episodes(self) -> Union[List[Episode], None]:
        """Returns the list of Episodes in this Show or None if no Episodes
        should exist (i.e. only Seasons must exist)
        """
        if self.__episodes is not None:
            return [episode for episode in self.__episodes]
        return self.__episodes

    def get_runtime(self, in_hours: bool = False) -> int:
        """Returns the runtime of this Show in hours or minutes

        :param in_hours: Whether or not to get the runtime in hours
        """
        if in_hours:
            return round(self.get_runtime() // 60)
        if self.get_seasons() is not None:
            return sum([season.get_runtime() for season in self.get_seasons()])
        return sum([episode.get_runtime() for episode in self.get_episodes()])

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def to_json(self) -> dict:
        """Returns a JSON representation of this Show object"""
        return {
            "id": self.get_id(),
            "name": self.get_name(),
            "provider": self.get_provider(),
            "person": self.get_person(),
            "started": self.is_started(),
            "finished": self.is_finished(),
            "seasons": [
                season.to_json()
                for season in self.get_seasons()
            ] if self.get_seasons() is not None else [],
            "episodes": [
                episode.to_json()
                for episode in self.get_episodes()
            ] if self.get_episodes() is not None else []
        }

    def save(self):
        """Saves this Show object into a JSON file"""
        if not os.path.exists(Show.FOLDER):
            os.mkdir(Show.FOLDER)
        with open("./{}/{}.json".format(Show.FOLDER, self.get_id()), "w") as jsonfile:
            dump(self.to_json(), jsonfile, indent=4)
