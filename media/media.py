from json import load
from uuid import uuid4

from exceptions import InvalidFormatError


class Media:
    """A Media object is a superclass for all types of Media
    including Movies, TV Shows, Limited Series, and Podcasts

    :param name: The name of this Media
    :param provider: The name of the streaming provider this Media is located on
    :param person: The person that is watching this Media

    :keyword started: Whether or not this Media has been started (Defaults to False)
    :keyword finished: Whether or not this Media has been finished (Defaults to False)
    :keyword json: The JSON object to load a Media object from
    :keyword filename: The JSON or CSV file to load a Media object from

    :raises FileNotFoundError: When the JSON or CSV file cannot be found
    :raises KeyError: When the required parameters are missing from the JSON object
    :raises ValueError: When any of the parameters have invalid values
    :raises InvalidFormatError: When the file type is not .json or .csv
    """

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, name: str = None,
                 provider: str = None,
                 person: str = None,
                 *, started: bool = False, finished: bool = False,
                 json: dict = None, filename: str = None):

        media_id = None  # Give the ID some default value

        # Check if a JSON or CSV file was given
        if filename is not None:
            if filename.endswith(".json"):
                with open(filename, "r") as jsonfile:
                    json = load(jsonfile)
            elif filename.endswith(".csv"):
                with open(filename, "r") as csvfile:
                    pass
            else:
                raise InvalidFormatError("File type must be .json or .csv")

        # Check if a JSON object was given
        if json is not None:
            if not {"id", "name", "provider", "person"}.issubset(set(json.keys())):
                raise KeyError("ID, Name, Provider, and Person must be specified")

            media_id = str(json["id"])
            name = json["name"]
            provider = json["provider"]
            person = json["person"]
            started = False if "started" not in json else json["started"]
            finished = False if "finished" not in json else json["finished"]

        # Validate the parameters values
        if name is None:
            raise ValueError("The name must be specified")
        if provider is None:
            raise ValueError("The Streaming Provider must be specified")
        if person is None:
            raise ValueError("The Person must be specified")
        if started is None:
            started = False
        if finished is None:
            finished = False

        if media_id is not None and len(media_id) == 0:
            raise ValueError("The ID must have a length > 0")
        if len(name) == 0:
            raise ValueError("The name must have a length > 0")
        if len(provider) == 0:
            raise ValueError("The streaming provider must have a length > 0")
        if len(person) == 0:
            raise ValueError("The person's name must have a length > 0")
        if started and finished:
            raise ValueError("This media cannot be started and finished at the same time")

        self.__id = str(uuid4()) if media_id is None else media_id
        self.__name = name
        self.__provider = provider
        self.__person = person
        self.__started = started
        self.__finished = finished

    def __eq__(self, media: 'Media'):
        if not isinstance(media, Media):
            return False
        return (media.get_name() == self.get_name() and
                media.get_provider() == self.get_provider() and
                media.get_person() == self.get_person() and
                media.is_started() is self.is_started() and
                media.is_finished() is self.is_finished())

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_id(self) -> str:
        """Returns the ID of this Media object"""
        return self.__id

    def get_name(self) -> str:
        """Returns the name of this Media object"""
        return self.__name

    def get_provider(self) -> str:
        """Returns the streaming provider where this Media object is located"""
        return self.__provider

    def get_person(self) -> str:
        """Returns the person who is watching this Media"""
        return self.__person

    def is_started(self) -> bool:
        """Returns whether or not this Media has been started"""
        return self.__started

    def is_finished(self) -> bool:
        """Returns whether or not this Media has been finished"""
        return self.__finished

    def get_runtime(self, in_hours: bool = False) -> int:
        """Returns the runtime of this media"""
        raise NotImplementedError()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def set_id(self, id: str):
        """Sets the ID for this Media object"""
        self.__id = id

    def set_name(self, name: str):
        """Sets the name for this Media object"""
        self.__name = name

    def set_provider(self, provider: str):
        """Sets the streaming provider for this Media object"""
        self.__provider = provider

    def set_person(self, person: str):
        """Sets the person watching this Media object"""
        self.__person = person

    def set_started(self, started: bool):
        """Sets whether or not this Media object has been started"""
        if started and self.is_finished():
            self.set_finished(False)
        self.__started = started

    def set_finished(self, finished: bool):
        """Sets whether or not this Media object has been finished"""
        if finished and self.is_started():
            self.set_started(False)
        self.__finished = finished

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def to_csv(self) -> str:
        """Returns the CSV representation of this Media object"""
        raise NotImplementedError()

    def to_json(self) -> dict:
        """Returns the JSON representation of this Media object"""
        raise NotImplementedError()

    def save(self):
        """Saves this Media object into a JSON file"""
        raise NotImplementedError()
