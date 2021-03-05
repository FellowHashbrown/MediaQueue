import os
import string
from datetime import datetime
from json import dumps
from typing import List, Union

from media import Media, Movie, TVShow, Podcast, LimitedSeries

EXPORTS = "exports"


def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are
    removed. Also spaces are replaced with underscores.

    Note: this method may produce invalid filenames such as ``, `.` or `..`
    When I use this method I prepend a date string like '2009_01_15_19_46_32_'
    and append a file extension like '.txt', so I avoid the potential of using
    an invalid filename.

    Pulled from https://gist.github.com/seanh/93666
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename


def __media_to(media: Union[List[Media], Movie, LimitedSeries, Podcast, TVShow],
               *, as_csv: bool = False, as_json: bool = False):
    """Exports the specified media into the specified file into the exports folder.

    Note that if as_csv and as_json are both False, nothing will happen and
    no exceptions will be raised.

    :param media: The Media object to convert into CSV or JSON
    :param as_csv: Whether or not to export the Media as a CSV file
    :param as_json: Whether or not to export the Media as a JSON file
    """

    # Create the exports folder if necessary
    if not os.path.exists(EXPORTS):
        os.mkdir(EXPORTS)

    # Get the filename
    now = datetime.now()
    file_location = "{}_{}_{}_{}_{}_{}_{}".format(
        now.year, now.month, now.day,
        now.hour, now.minute, now.second,
        format_filename(media.get_name())
        if not isinstance(media, List) else "all_media")

    # Export media as CSV
    if as_csv:
        if isinstance(media, List):
            csv_object = "\n".join(m.to_csv() for m in media)
        else:
            csv_object = media.to_csv()
        with open(f"./exports/{file_location}.csv", "w") as csv_file:
            csv_file.write(csv_object)

    # Export media as JSON
    if as_json:
        json_object = []
        if isinstance(media, List):
            for m in media:
                json_object.append(m.to_json())
        else:
            json_object = media.to_json()
        with open(f"./exports/{file_location}.json", "w") as json_file:
            json_file.write(dumps(json_object, indent=4))


def media_to_csv(media: Union[List[Media], Movie, LimitedSeries, Podcast, TVShow]):
    """Exports the specified media into a CSV file

    :param media: The Media object to convert into CSV
    """
    __media_to(media, as_csv=True)


def media_to_json(media: Union[List[Media], Movie, LimitedSeries, Podcast, TVShow]):
    """Exports the specified media into a JSON file

    :param media: The Media object to convert into JSON
    """
    __media_to(media, as_json=True)
