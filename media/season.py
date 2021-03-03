from typing import List

from media import Episode


class Season:
    """A Season is part of a Show which holds Episodes in the Show.

    This can also be loaded from a JSON object.

    :param season: The number of the Season
    :param episodes: The list of Episodes in this Season

    :keyword json: The JSON object of a Season to load from

    :raises KeyError: When the season and episodes parameters are missing
    :raises ValueError: When the parameter values are invalid
    """

    def __init__(self, season: int = None, episodes: List[Episode] = None,
                 *, json: dict = None):

        # Check if the JSON object is given
        if json is not None:
            if {"season", "episodes"} != set(json.keys()):
                raise KeyError("Season and Episodes must be given")

            season = json["season"]
            episodes = [Episode(json=episode) for episode in json["episodes"]]

        # The JSON object was not given
        # load from the parameters
        if episodes is None:
            episodes = []
        if season is None:
            raise ValueError("Season must be given")
        if season <= 0:
            raise ValueError("Season must be > 0")

        self.__season = season
        self.__episodes = [episode for episode in episodes]

    def __str__(self):
        return "Season({}, {})".format(
            self.get_season(),
            ", ".join([str(episode) for episode in self.get_episodes()])
        )

    def __eq__(self, season: 'Season'):
        if not isinstance(season, Season):
            return False
        return (season.get_season() == self.get_season() and
                {season.get_episodes()} == {self.get_episodes()})

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_season(self) -> int:
        """Return the season number"""
        return self.__season

    def get_episodes(self) -> List[Episode]:
        """Returns a list of Episodes in this Season"""
        return [episode for episode in self.__episodes]

    def get_runtime(self, in_hours: bool = False) -> int:
        """Returns the runtime of this Season in hours or minutes

        :param in_hours: Whether or not to get the runtime in hours
        """
        if in_hours:
            return round(self.get_runtime() // 60)
        return sum([episode.get_runtime() for episode in self.get_episodes()])

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def to_json(self) -> dict:
        """Returns the JSON representation of this Season"""
        return {
            "season": self.get_season(),
            "episodes": [episode.to_json() for episode in self.get_episodes()]
        }
