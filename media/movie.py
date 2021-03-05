import os
from json import dump, load
from typing import Union

from media import Media, StreamingProvider, Person


class Movie(Media):
    """A Movie object is a single type of media

    :param name: The name of the Movie
    :param runtime: The runtime of this Movie in minutes
    :param provider: The Streaming Provider where this Movie is located on
    :param person: The Person that is watching this Movie

    :keyword started: Whether or not this Movie has been started (Defaults to False)
    :keyword finished: Whether or not this Movie has been finished (Defaults to False)
    :keyword json: The JSON object to load a Movie object from
    :keyword filename: The JSON file to load a Movie object from

    :raises FileNotFoundError: When the JSON file specified does not exist
    :raises KeyError: When any required parameters are missing
    :raises ValueError: When any parameters do not have a valid value
    """

    FOLDER = "movies"

    def __init__(self, name: str = None, runtime: int = None,
                 provider: Union[StreamingProvider, str] = None,
                 person: Union[Person, str] = None,
                 *, started: bool = False, finished: bool = False,
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
            if "runtime" not in json:
                raise KeyError("Runtime must be specified")

            runtime = json["runtime"]

        # Validate the parameters values
        if runtime is None:
            raise ValueError("Runtime must be specified")

        if runtime is not None and runtime <= 0:
            raise ValueError("Runtime must be > 0")

        self.__runtime = runtime

    def __str__(self):
        return "Movie({}, {}, {}, {}, {}, {}, {})".format(
            self.get_id(),
            self.get_name(), self.get_runtime(),
            self.get_provider().value, self.get_person().value,
            "Started" if self.is_started() else "Not Started",
            "Finished" if self.is_finished() else "Not finished"
        )

    def __eq__(self, movie: 'Movie'):
        if not isinstance(movie, Movie):
            return False
        return (movie.get_name() == self.get_name() and
                movie.get_runtime() == self.get_runtime() and
                movie.get_provider() == self.get_provider() and
                movie.get_person() == self.get_person() and
                movie.is_started() is self.is_started() and
                movie.is_finished() is self.is_finished())

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_runtime(self, in_hours: bool = False) -> int:
        """Returns the runtime of this Movie in minutes or hours

        :param in_hours: Whether or not to get the runtime in hours
        """
        if in_hours:
            return round(self.get_runtime() // 60)
        return self.__runtime

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def to_csv(self) -> str:
        """Returns the CSV representation of this Movie"""
        return "\"{}\",{},{},{},{},{}".format(
            self.get_name(), self.get_runtime(),
            self.get_provider().value, self.get_person().value,
            self.is_started(), self.is_finished()
        )

    def to_json(self) -> dict:
        """Returns the JSON representation of this Movie"""
        return {
            "id": self.get_id(),
            "name": self.get_name(),
            "runtime": self.get_runtime(),
            "provider": self.get_provider().value,
            "person": self.get_person().value,
            "started": self.is_started(),
            "finished": self.is_finished()
        }

    def save(self):
        """Saves this Movie into a JSON file"""
        if not os.path.exists(f"./data/{Movie.FOLDER}"):
            os.mkdir(f"./data/{Movie.FOLDER}")
        with open("./data/{}/{}.json".format(Movie.FOLDER, self.get_id()), "w") as jsonfile:
            dump(self.to_json(), jsonfile, indent=4)
