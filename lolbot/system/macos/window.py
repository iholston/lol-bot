from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID

GAME_WINDOW = 'League of Legends (TM) Client'
CLIENT_WINDOW = 'League of Legends'


class WindowNotFound(Exception):
    pass


def check_window_exists(window_name: str):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for window in windows:
        if window['kCGWindowOwnerName'] == window_name:
            return True
    raise WindowNotFound


def get_window_size(window_name: str):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for window in windows:
        if window['kCGWindowOwnerName'] == window_name:
            bounds = window.get('kCGWindowBounds', {})
            x = bounds.get('X')
            y = bounds.get('Y')
            h = bounds.get('Height')
            w = bounds.get('Width')
            return x, y, h, w
    raise WindowNotFound


def convert_ratio(ratio: tuple, window_name: str):
    x, y, h, w = get_window_size(window_name)
    updated_x = ((w - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    return updated_x, updated_y
