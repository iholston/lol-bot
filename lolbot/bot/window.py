"""
Utility functions for determining if a window exists.
"""

from win32gui import FindWindow, GetWindowRect

CLIENT_WINDOW_NAME = "League of Legends"
GAME_WINDOW_NAME = "League of Legends (TM) Client"


class WindowNotFound(Exception):
    pass


def game_window_exists() -> bool:
    """Checks if the league of legends game window exists"""
    if FindWindow(None, GAME_WINDOW_NAME) == 0:
        return False
    return True


def client_window_exists() -> bool:
    """Checks if the league of legends client window exists"""
    if FindWindow(None, CLIENT_WINDOW_NAME) == 0:
        return False
    return True


def window_exists(window_title: str) -> bool:
    """Checks if a window exists"""
    if FindWindow(None, window_title) == 0:
        return False
    return True


def get_window_size(window_title: str) -> tuple:
    """Gets the size of an open window"""
    window_handle = FindWindow(None, window_title)
    if window_handle == 0:
        raise WindowNotFound
    window_rect = GetWindowRect(window_handle)
    return window_rect[0], window_rect[1], window_rect[2], window_rect[3]
