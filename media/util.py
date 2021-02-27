from typing import List, Type, Union

from media import Media, LimitedSeries, Podcast, TVShow, Movie


def get_type(media: Union[Media, str] = None,
             reverse: bool = False) -> Union[List[str], Type[Media],
                                             Type[LimitedSeries], Type[Movie],
                                             Type[Podcast], Type[TVShow],
                                             str, type(None)]:
    """Returns the type of Media specified

    :param media: The media type or str of the type of media
    :param reverse: Whether or not to get the class
    """

    if not reverse:
        if isinstance(media, Movie):
            return "Movie"
        if isinstance(media, LimitedSeries):
            return "Limited Series"
        if isinstance(media, Podcast):
            return "Podcast"
        if isinstance(media, TVShow):
            return "TV Show"
        if media is None:
            return ["Movie", "TV Show", "Podcast", "Limited Series"]
        return "Unknown"
    else:
        if media == "Movie":
            return Movie
        if media == "TV Show":
            return TVShow
        if media == "Podcast":
            return Podcast
        if media == "Limited Series":
            return LimitedSeries
        if media == "All":
            return Media
        return None
