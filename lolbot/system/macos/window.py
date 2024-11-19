from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID

GAME_WINDOW = 'League Of Legends'
CLIENT_WINDOW = 'League of Legends'


class WindowNotFound(Exception):
    pass


def check_window_exists(window_name: str):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for window in windows:
        if window['kCGWindowOwnerName'] == window_name:
            bounds = window.get('kCGWindowBounds', {})
            if bounds.get('X') > 0 and bounds.get('Y') > 0:
                return True
    raise WindowNotFound


def get_window_size(window_name: str):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for window in windows:
        if window['kCGWindowOwnerName'] == window_name:
            bounds = window.get('kCGWindowBounds', {})
            x = bounds.get('X')
            y = bounds.get('Y')
            l = bounds.get('Width')
            h = bounds.get('Height')
            if x != 0 and y != 0:
                return x, y, l, h
    raise WindowNotFound


def convert_ratio(ratio: tuple, window_name: str):
    x, y, l, h = get_window_size(window_name)
    updated_x = (l * ratio[0]) + x
    updated_y = (h * ratio[1]) + y
    return updated_x, updated_y
