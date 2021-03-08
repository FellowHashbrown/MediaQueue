from functools import cmp_to_key
from typing import List

from media import Media, Episode, Movie, TVShow, Podcast, LimitedSeries
from media.util import get_type


class MediaObjects:
    """The Media Objects class, and instance, exists to ease
    receiving and sending media object data back and forth between
    different views such as between the Home and TV Show/Podcast/Limited Series/Movie
    and from the TV Show/Podcast/Limited Series to Episode dialog
    """

    def __init__(self):
        self.__episode = None
        self.__episodes = []
        self.__removed_episodes = []
        self.__filtered_episodes = []
        self.__limited_series = None
        self.__tv_show = None
        self.__podcast = None
        self.__movie = None
        self.__media = []
        self.__removed_media = []
        self.__filtered_media = []

        self.__episode_filter = {"season": None, "watched": None}
        self.__media_filter = {
            "started": None, "finished": None,
            "type": None, "provider": None,
            "person": None, "search": None}

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def set_episode(self, episode: Episode = None):
        """Sets the Episode to be remembered

        :param episode: The Episode to remember.
            If set to None, it will clear the episode
        """
        self.__episode = episode

    def set_episodes(self, episodes: List[Episode] = None):
        """Sets the list of Episodes to be remembered

        :param episodes: The list of Episodes to remember.
            If set to None, it will clear the Episodes
        """
        if episodes is None:
            episodes = []
        self.__episodes = episodes

    def set_removed_episodes(self, removed_episodes: List[int] = None):
        """Sets the list of Removed Episodes to be remembered

        :param removed_episodes: The list of Removed Episodes to remember.
            If set to None, it will clear the Removed Episodes
        """
        if removed_episodes is None:
            removed_episodes = []
        self.__removed_episodes = removed_episodes

    def set_limited_series(self, limited_series: LimitedSeries = None):
        """Sets the Limited Series to be remembered.

        :param limited_series: The Limited Series to remember.
            If set to None, it will clear the Limited Series
        """
        self.__limited_series = limited_series

    def set_tv_show(self, tv_show: TVShow = None):
        """Sets the TV Show to be remembered.

        :param tv_show: The TV Show to remember.
            If set to None, it will clear the TV Show
        """
        self.__tv_show = tv_show

    def set_podcast(self, podcast: Podcast = None):
        """Sets the Podcast to be remembered.

        :param podcast: The Podcast to remember.
            If set to None, it will clear the Podcast
        """
        self.__podcast = podcast

    def set_movie(self, movie: Movie = None):
        """Sets the Movie to be remembered.

        :param movie: The Movie to remember.
            If set to None, it will clear the Movie
        """
        self.__movie = movie

    def set_media(self, media: List[Media] = None):
        """Sets the list of Media to be remembered.

        :param media: The list of Media to remember.
            If set to None, it will clear the Media
        """
        self.__media = media

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_episode(self) -> Episode:
        """Returns the remembered Episode"""
        return self.__episode

    def get_episodes(self) -> List[Episode]:
        """Returns the remembered list of Episodes"""
        return self.__episodes

    def get_removed_episodes(self) -> List[Episode]:
        """Returns the remembered list of removed Episodes"""
        return self.__removed_episodes

    def get_filtered_episodes(self) -> List[Episode]:
        """Returns the filtered Episodes based off the Episode Filter"""
        self.filter_episodes()
        return self.__filtered_episodes

    def get_limited_series(self) -> LimitedSeries:
        """Returns the remembered Limited Series"""
        return self.__limited_series

    def get_tv_show(self) -> TVShow:
        """Returns the remembered TV Show"""
        return self.__tv_show

    def get_podcast(self) -> Podcast:
        """Returns the remembered Podcast"""
        return self.__podcast

    def get_movie(self) -> Movie:
        """Returns the remembered Movie"""
        return self.__movie

    def get_media(self) -> List[Media]:
        """Returns the remembered Media"""
        return self.__media

    def get_removed_media(self) -> List[Media]:
        """Returns the remembered list of Removed Media"""
        return self.__removed_media

    def get_filtered_media(self) -> List[Media]:
        """Returns the filtered Media based off the Media Filter"""
        self.filter_media()
        return self.__filtered_media

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def set_episode_filters(self, *, season: int = None, watched: bool = None):
        """Sets the filters for the episodes

        :keyword season: The season to filter episodes by.
            If set to None, it will show episodes from all seasons
        :keyword watched: Whether to get watched or unwatched episodes.
            If set to None, it will show all episodes, regardless of their watched status
        """
        self.__episode_filter["season"] = season
        self.__episode_filter["watched"] = watched
        self.filter_episodes()

    def filter_episodes(self):
        """Filters the saved episodes based off the filters specified by set_episodes_filters"""
        self.__filtered_episodes = []
        for i in range(len(self.get_episodes())):
            episode = self.get_episodes()[i]
            if i in self.get_removed_episodes():
                continue
            if self.__episode_filter["season"] is not None:
                if episode.get_season() != self.__episode_filter["season"]:
                    continue
            if self.__episode_filter["watched"] is not None:
                if episode.is_watched() is not self.__episode_filter["watched"]:
                    continue
            self.__filtered_episodes.append(episode)

    def sort_episodes(self):
        """Sorts the Episodes in the list by Season Number and Episode Number"""

        def sort_key(a: Episode, b: Episode):
            """The sort function"""
            if a.get_season() == b.get_season():
                if a.get_episode() == b.get_episode():
                    return 0
                return a.get_episode() - b.get_episode()
            return a.get_season() - b.get_season()

        self.__episodes = sorted([
            episode
            for episode in self.__episodes
            if episode is not None
        ], key=cmp_to_key(sort_key))

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def set_media_filters(self, *, started: bool = None, finished: bool = None,
                          media_type: Media = None, provider: str = None,
                          person: str = None, search: str = None):
        """Sets the filters for the Media on the Home screen

        :keyword started: The started filter to use. (Defaults to None)
        :keyword finished: The finished filter to use. (Defaults to None)
        :keyword media_type: The media type filter to use. (Defaults to None)
        :keyword provider: The provider filter to use. (Defaults to None)
        :keyword person: The person filter to use. (Defaults to None)
        :keyword search: The search filter to use. (Defaults to None)
        """

        self.__media_filter["started"] = started
        self.__media_filter["finished"] = finished
        self.__media_filter["type"] = media_type
        self.__media_filter["provider"] = provider
        self.__media_filter["person"] = person
        self.__media_filter["search"] = search
        self.filter_media()

    def filter_media(self):
        """Applies the filters for the Media to
        the current list of Media
        """

        self.__filtered_media = []
        for i in range(len(self.get_media())):
            medium = self.get_media()[i]
            if i in self.get_removed_media():
                continue
            if self.__media_filter["search"] is not None:
                if self.__media_filter["search"].lower() not in medium.get_name().lower():
                    continue
            if self.__media_filter["started"] is not None:
                if self.__media_filter["started"] is not medium.is_started():
                    continue
            if self.__media_filter["finished"] is not None:
                if self.__media_filter["finished"] is not medium.is_finished():
                    continue
            if self.__media_filter["type"] is not None:
                if self.__media_filter["type"] != get_type(medium):
                    continue
            if self.__media_filter["provider"] is not None:
                if self.__media_filter["provider"] != medium.get_provider():
                    continue
            if self.__media_filter["person"] is not None:
                if self.__media_filter["person"] != medium.get_person():
                    continue
            self.__filtered_media.append(medium)

    def sort_media(self):
        """Sorts the Media in the list by Type, Provider, Person, and Name"""

        def sort_key(a, b):
            """A local function meant to be used as a sorting key"""

            # Types are the same, move to Provider
            if get_type(a) == get_type(b):

                # Providers are the same, move to Person
                if a.get_provider() == b.get_provider():

                    # Persons are the same, move to name
                    if a.get_person() == b.get_person():

                        if a.get_name() == b.get_name():
                            return 0
                        elif a.get_name() < b.get_name():
                            return -1
                        return 1

                    # Persons are different
                    elif a.get_person() < b.get_person():
                        return -1
                    return 1

                # Providers are different
                elif a.get_provider() < b.get_provider():
                    return -1
                return 1

            # Types are different
            elif get_type(a) < get_type(b):
                return -1
            return 1

        self.__media = sorted(self.__media, key=cmp_to_key(sort_key))


# Create an instance of the MediaObjects to use across classes
media_objects = MediaObjects()
