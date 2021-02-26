class Episode:
    """An Episode is part of a Season, a Limited Series, or a Podcast.

    This can also be loaded from a JSON object.

    :param season: The season number this Episode belongs to
    :param episode: The episode number
    :param name: The name of this Episode
    :param runtime: The runtime of this Episode
    :param json: The JSON object of an Episode to load from
    """

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, season: int = None, episode: int = None,
                 name: str = None, runtime: int = None,
                 *, watched: bool = False, json: dict = None):

        # Check if the JSON object is given
        if json is not None:
            if {"season", "episode", "name", "runtime"}.issubset(set(json.keys())):
                raise KeyError("Season, Episode, Name, and Runtime must be given")

            season = json["season"]
            episode = json["episode"]
            name = json["name"]
            runtime = json["runtime"]
            watched = False if "watched" not in json else json["watched"]

        # The JSON object was not given
        # load from the parameters
        if not all([season is not None, episode is not None,
                    name is not None, runtime is not None]):
            raise ValueError("Season, Episode, Name, and Runtime must be given")
        if season <= 0:
            raise ValueError("Season must be > 0")
        if episode <= 0:
            raise ValueError("Episode must be > 0")
        if runtime <= 0:
            raise ValueError("Runtime must be > 0")
        if len(name) == 0:
            raise ValueError("Name must have length > 0")

        self.__season = season
        self.__episode = episode
        self.__name = name
        self.__runtime = runtime
        self.__watched = watched

    def __eq__(self, episode: 'Episode'):
        if not isinstance(episode, Episode):
            return False
        return (episode.get_season() == self.get_season() and
                episode.get_episode() == self.get_episode() and
                episode.get_name() == self.get_name() and
                episode.get_runtime() == self.get_runtime() and
                episode.is_watched() == self.is_watched())

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_season(self) -> int:
        """Returns the season number this Episode belongs to"""
        return self.__season

    def get_episode(self) -> int:
        """Returns this Episode number"""
        return self.__episode

    def get_name(self) -> str:
        """Returns the name of this Episode"""
        return self.__name

    def get_runtime(self) -> int:
        """Returns the runtime of this Episode"""
        return self.__runtime

    def is_watched(self) -> bool:
        """Returns whether or not this Episode has been watched"""
        return self.__watched

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def to_json(self) -> dict:
        """Returns the JSON representation of this Episode"""
        return {
            "season": self.get_season(),
            "episode": self.get_episode(),
            "name": self.get_name(),
            "runtime": self.get_runtime(),
            "watched": self.is_watched()
        }
