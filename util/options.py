import os
from json import dump, load
from typing import List


class MediaQueueOptions:
    """A class based around options for the Media Queue

    The current options include a list of Streaming Providers
    and the People to keep track of
    """

    def __init__(self):
        self.__providers = []
        self.__persons = []

        # Check if the options file exists
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.exists("data/options.json"):
            with open("data/options.json", "w") as options_file:
                dump({
                    "providers": ["Default"],
                    "persons": ["Default"]
                }, options_file)

        # Load the file
        with open("data/options.json", "r") as options_file:
            options = load(options_file)
            self.__providers = options["providers"]
            self.__persons = options["persons"]

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_providers(self) -> List[str]:
        """Returns the list of Providers in the options"""
        return self.__providers + ["Default", "Unavailable"]

    def get_persons(self) -> List[str]:
        """Returns the list of Persons in the options"""
        return self.__persons + ["Default"]

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
                "persons": self.__persons
            }, options_file, indent=4)


options = MediaQueueOptions()
