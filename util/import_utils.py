from csv import reader
from io import TextIOWrapper
from typing import List, Union

from media import StreamingProvider, Person
from media import Movie, LimitedSeries, Podcast, TVShow, Season, Episode


def csv_to_media(file: Union[TextIOWrapper, str]) -> List[Union[Movie, LimitedSeries, Podcast, TVShow]]:
    """Converts the specified CSV file or filename into a
    JSON object

    :param file: The file object or filename of the CSV file to load

    :raises FileNotFoundError: If the specified filename was not found on the system
    :raises TypeError: If the CSV file holds an unknown object type
    """

    # Load the CSV file and split into lines
    if isinstance(file, str):
        file = open(file, "r")
    r = reader(file)
    contents = [line for line in r if len(line) > 0]

    # Parse the lines to create Media objects from
    last = 0
    media_list = []
    content_list = []
    for i in range(len(contents)):
        line = contents[i]
        if line[0] in ["Movie", "LimitedSeries", "Podcast", "TVShow"]:
            media_content = contents[last:i]
            if len(media_content) > 0:
                content_list.append(media_content)
            last = i
    content_list.append(contents[last:])

    # Iterate through the content list to turn content into Media objects
    for media_content in content_list:

        if media_content[0][0] == "Movie":
            name, runtime, provider, person, started, finished = media_content[1]
            media_list.append(Movie(
                name, int(runtime),
                StreamingProvider(provider), Person(person),
                started=started == "True", finished=finished == "True"
            ))

        elif media_content[0][0] == "LimitedSeries":
            name, provider, person, started, finished = media_content[1]
            episodes = []
            for episode in media_content[2:]:
                s_num, e_num, e_name, runtime, watched = episode
                episodes.append(Episode(
                    int(s_num), int(e_num),
                    e_name, int(runtime),
                    watched=watched == "True"
                ))
            media_list.append(LimitedSeries(
                name, StreamingProvider(provider), Person(person), episodes,
                started=started == "True", finished=finished == "True"
            ))

        elif media_content[0][0] in ["Podcast", "TVShow"]:
            name, provider, person, started, finished = media_content[1]
            seasons = {}
            for episode in media_content[2:]:
                s_num, e_num, e_name, runtime, watched = episode
                if int(s_num) not in seasons:
                    seasons[int(s_num)] = []
                seasons[int(s_num)].append(Episode(
                    int(s_num), int(e_num),
                    name, int(runtime),
                    watched=watched == "True"
                ))
            seasons = [Season(season, seasons[season]) for season in seasons]

            if media_content[0][0] == "Podcast":
                media_list.append(Podcast(
                    name, StreamingProvider(provider), Person(person), seasons,
                    started=started == "True", finished=finished == "True"
                ))
            else:
                media_list.append(TVShow(
                    name, StreamingProvider(provider), Person(person), seasons,
                    started=started == "True", finished=finished == "True"
                ))
    return media_list
