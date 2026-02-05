from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionAll, kCGNullWindowID

GAME_WINDOW = 'League Of Legends'
CLIENT_WINDOW = 'League of Legends'


class WindowNotFound(Exception):
    pass


def _get_window_candidates(window_name: str):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    candidates = []
    for window in windows:
        if window.get('kCGWindowOwnerName') != window_name:
            continue
        bounds = window.get('kCGWindowBounds', {})
        x = bounds.get('X')
        y = bounds.get('Y')
        width = bounds.get('Width')
        height = bounds.get('Height')
        alpha = window.get('kCGWindowAlpha', 1)
        layer = window.get('kCGWindowLayer', 0)
        if x is None or y is None or width is None or height is None:
            continue
        candidates.append({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "alpha": alpha,
            "layer": layer,
        })
    return candidates


def _select_best_window(window_name: str):
    candidates = _get_window_candidates(window_name)
    if not candidates:
        raise WindowNotFound

    filtered = [
        window
        for window in candidates
        if window["width"] >= 400 and window["height"] >= 300 and window["alpha"] > 0
    ]

    if not filtered:
        filtered = candidates

    def area_key(item):
        return item["width"] * item["height"], item["alpha"], -item["layer"]

    return max(filtered, key=area_key)


def check_window_exists(window_name: str):
    window = _select_best_window(window_name)
    if window["x"] is not None and window["y"] is not None:
        return True
    raise WindowNotFound


def get_window_size(window_name: str):
    window = _select_best_window(window_name)
    return window["x"], window["y"], window["width"], window["height"]


def debug_window_bounds(window_name: str):
    """Returns selected window bounds for diagnostics."""
    return _select_best_window(window_name)


def convert_ratio(ratio: tuple, window_name: str):
    x, y, l, h = get_window_size(window_name)
    updated_x = (l * ratio[0]) + x
    updated_y = (h * ratio[1]) + y
    return updated_x, updated_y
