from enum import Enum


class StreamingProvider(Enum):
    """An Enumeration for Streaming Providers"""
    APPLE = "Apple"
    DISNEY = "Disney+"
    HBO_MAX = "HBO Max"
    HULU = "Hulu"
    NETFLIX = "Netflix"
    SPOTIFY = "Spotify"
    VUDU = "Vudu"
    UNAVAILABLE = "Unavailable"
