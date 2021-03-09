import os
import sys


def resource_path(relative_path: str):
    """Get the absolute path to the specified path which primarily applies to a
    single-file application

    :param relative_path: The path of the file to retrieve
    """
    # noinspection PyBroadException
    try:
        # noinspection PyProtectedMember,PyUnresolvedReferences
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
