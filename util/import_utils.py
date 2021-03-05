from csv import reader
from io import TextIOWrapper
from typing import Union

from media import StreamingProvider, Person
from media import Movie, LimitedSeries, Podcast, TVShow, Season, Episode


def csv_to_media(file: Union[TextIOWrapper, str]) -> Union[Movie, LimitedSeries, Podcast, TVShow]:
    """Converts the specified CSV file or filename into a
    JSON object

    :param file: The file object or filename of the CSV file to load

    :raises FileNotFoundError: If the specified filename was not found on the system
    :raises TypeError: If the CSV file holds an unknown object type
    """

    if isinstance(file, str):
        file = open(file, "r")
    r = reader(file)
    contents = [line for line in r if len(line) > 0]
    if contents[0][0] == "Movie":
        name, runtime, provider, person, started, finished = contents[1]
        return Movie(
            name, int(runtime),
            StreamingProvider(provider), Person(person),
            started=started == "True", finished=finished == "True"
        )
    elif contents[0][0] == "LimitedSeries":
        name, provider, person, started, finished = contents[1]
        episodes = []
        for episode in contents[2:]:
            s_num, e_num, e_name, runtime, watched = episode
            episodes.append(Episode(
                int(s_num), int(e_num),
                e_name, int(runtime),
                watched=watched == "True"
            ))
        return LimitedSeries(
            name, StreamingProvider(provider), Person(person), episodes,
            started=started == "True", finished=finished == "True"
        )
    elif contents[0][0] in ["Podcast", "TVShow"]:
        name, provider, person, started, finished = contents[1]
        seasons = {}
        for episode in contents[2:]:
            s_num, e_num, e_name, runtime, watched = episode
            if int(s_num) not in seasons:
                seasons[int(s_num)] = []
            seasons[int(s_num)].append(Episode(
                int(s_num), int(e_num),
                name, int(runtime),
                watched=watched == "True"
            ))
        seasons = [Season(season, seasons[season]) for season in seasons]
        if contents[0][0] == "Podcast":
            return Podcast(
                name, StreamingProvider(provider), Person(person), seasons,
                started=started == "True", finished=finished == "True"
            )
        return TVShow(
            name, StreamingProvider(provider), Person(person), seasons,
            started=started == "True", finished=finished == "True"
        )
    raise TypeError("The specified CSV file does not match known media")
