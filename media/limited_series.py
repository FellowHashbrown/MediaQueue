import os
from json import dump
from typing import List

from media import Episode, Show
from options import options


class LimitedSeries(Show):
    """A LimitedSeries is a Show that has only 1 Season of Episodes.
    In this, only the Episodes need to be specified

    :param name: The name of this LimitedSeries
    :param episodes: A list of Episodes in this LimitedSeries
    :param provider: The name of the streaming provider this LimitedSeries is located on
    :param person: The person that is watching this LimitedSeries

    :keyword started: Whether or not this LimitedSeries has been started (Defaults to False)
    :keyword finished: Whether or not this LimitedSeries has been finished (Defaults to False)
    :keyword json: The JSON object to load a LimitedSeries object from
    :keyword filename: The JSON file to load a LimitedSeries object from

    :raises FileNotFoundError: When the JSON file cannot be found
    :raises KeyError: When the required parameters are missing from the JSON object
    """

    FOLDER = "limitedSeries"

    def __init__(self, name: str = None, provider: str = None,
                 person: str = None, episodes: List[Episode] = None,
                 *, started: bool = False, finished: bool = False,
                 json: dict = None, filename: str = None):
        super().__init__(name, provider, person,
                         episodes=episodes,
                         started=started, finished=finished,
                         json=json, filename=filename)

    def __str__(self):
        return "LimitedSeries({}, {}, {}, {}, {}, {}, {})".format(
            self.get_id(), self.get_name(),
            self.get_provider(), self.get_person(),
            "Started" if self.is_started() else "Not Started",
            "Finished" if self.is_finished() else "Not Finished",
            ", ".join([str(episode) for episode in self.get_episodes()])
        )

    def __eq__(self, limited_series: 'LimitedSeries'):
        if not isinstance(limited_series, LimitedSeries):
            return False
        return (limited_series.get_name() == self.get_name() and
                {limited_series.get_episodes()} == {self.get_episodes()} and
                limited_series.get_provider() == self.get_provider() and
                limited_series.get_person() == self.get_person() and
                limited_series.is_started() is self.is_started() and
                limited_series.is_finished() is self.is_finished())

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def to_csv(self) -> str:
        """Returns the CSV representation of this LimitedSeries object"""
        show_csv = "\"{}\",{},{},{},{}".format(
            self.get_name(), self.get_provider(),
            self.get_person(),
            self.is_started(), self.is_finished()
        )
        episodes_csv = "\n".join(episode.to_csv() for episode in self.get_episodes())
        return f"LimitedSeries\n{show_csv}\n{episodes_csv}"

    def to_json(self) -> dict:
        """Returns the JSON representation of this LimitedSeries object"""
        super_json = super().to_json()
        super_json.pop("seasons")   # A limited series shouldn't have Seasons
        return super_json

    def save(self):
        """Saves this LimitedSeries object into a JSON file"""
        if not os.path.exists(f"{options.get_base_dir()}/data"):
            os.mkdir(f"{options.get_base_dir()}/data")
        if not os.path.exists(f"{options.get_base_dir()}/data/{LimitedSeries.FOLDER}"):
            os.mkdir(f"{options.get_base_dir()}/data/{LimitedSeries.FOLDER}")
        with open("{}/data/{}/{}.json".format(options.get_base_dir(), LimitedSeries.FOLDER, self.get_id()), "w") as jsonfile:
            dump(self.to_json(), jsonfile, indent=4)
