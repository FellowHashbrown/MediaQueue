import os
from json import dump, load
from typing import List


class MediaQueueOptions:
    """A class based around options for the Media Queue

    The current options include a list of Streaming Providers
    and the People to keep track of
    """

    __instance = None

    @staticmethod
    def get_instance():
        if MediaQueueOptions.__instance is None:
            MediaQueueOptions()
        return MediaQueueOptions.__instance

    def __init__(self):

        if MediaQueueOptions.__instance is not None:
            raise TypeError("An instance of MediaQueueOptions already exists! Use .get_instance()")
        else:
            MediaQueueOptions.__instance = self
        self.__providers = []
        self.__persons = []
        self.__base_dir = None

        # Check if the options file exists
        if not os.path.exists("./options.json"):
            with open("./options.json", "w") as options_file:
                dump({
                    "providers": [],
                    "persons": [],
                    "base_dir": self.__base_dir
                }, options_file, indent=4)

        # Load the file
        with open("./options.json", "r") as options_file:
            options_json = load(options_file)
            self.__providers = options_json["providers"]
            self.__persons = options_json["persons"]
            self.__base_dir = options_json["base_dir"]

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_providers(self) -> List[str]:
        """Returns the list of Providers in the options"""
        return self.__providers + ["Default", "Unavailable"]

    def get_persons(self) -> List[str]:
        """Returns the list of Persons in the options"""
        return self.__persons + ["Default"]

    def get_base_dir(self) -> str:
        """Returns the base directory of where the user wants their data to go"""
        return self.__base_dir

    def set_base_dir(self, base_dir: str):
        """Sets the base directory to store all the data"""
        self.__base_dir = base_dir
        self.save()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def add_provider(self, provider: str) -> bool:
        """Adds a new Streaming Provider to the options
        and returns if the addition was successful

        :param provider: The Streaming Provider to add
        """
        for p in self.get_providers():
            if p.lower() == provider.lower():
                return False
        self.__providers.append(provider)
        self.__providers.sort()
        self.save()
        return True

    def add_person(self, person: str) -> bool:
        """Adds a new Person to the options
        and returns if the addition was successful

        :param person: The Person to add
        """
        for p in self.get_persons():
            if p.lower() == person.lower():
                return False
        self.__persons.append(person)
        self.__persons.sort()
        self.save()
        return True

    def remove_provider(self, index: int) -> bool:
        """Removes a Streaming Provider from the options
        and returns if the removal was successful

        :param index: The index of the Streaming Provider to remove
        """
        if index >= len(self.__providers):
            return False
        self.__providers.pop(index)
        self.save()
        return True

    def remove_person(self, index: int) -> bool:
        """Removes a Person from the options
        and returns if the removal was successful

        :param index: The index of the Streaming Provider to remove
        """
        if index >= len(self.__persons):
            return False
        self.__persons.pop(index)
        self.save()
        return True

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def save(self):
        """Saves the options into the json file"""
        with open("data/options.json", "w") as options_file:
            dump({
                "providers": self.__providers,
                "persons": self.__persons,
                "base_dir": self.__base_dir
            }, options_file, indent=4)


options = MediaQueueOptions.get_instance()
