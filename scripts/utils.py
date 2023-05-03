import keyboard
import pyautogui
import mouse
import logging
from time import sleep
from win32gui import FindWindow, GetWindowRect
from constants import *

log = logging.getLogger(__name__)

# Window
class WindowNotFound(Exception):
    pass

def screenshot(img_name, path=''):
    im = pyautogui.screenshot()
    if not path:
        im.save(os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + img_name + ".png")
    else:
        im.save(path + img_name)

def size(window_title=LEAGUE_CLIENT_WINNAME):
    window_handle = FindWindow(None, window_title)
    if window_handle == 0:
        raise WindowNotFound
    window_rect = GetWindowRect(window_handle)
    return window_rect[0], window_rect[1], window_rect[2], window_rect[3]

def exists(window_title):
    log.debug("Checking if {} window exists".format(window_title))
    if FindWindow(None, window_title) == 0:
        return False
    return True

# Mouse
def click(ratio, expected_window_name='', wait=1):
    # Window selection
    if expected_window_name != '' and not exists(expected_window_name):
        log.debug("Cannot click on {}, {} does not exist".format(ratio, expected_window_name))
        raise WindowNotFound
    elif expected_window_name != '':
        window_name = expected_window_name
    else:  # check if game is running and default to game otherwise set window to league client
        if exists(LEAGUE_GAME_CLIENT_WINNAME):
            window_name = LEAGUE_GAME_CLIENT_WINNAME
        elif exists(LEAGUE_CLIENT_WINNAME):
            window_name = LEAGUE_CLIENT_WINNAME
        else:
            log.debug("Cannot click on {}, no available window".format(ratio))
            return

    # Click
    log.debug('Clicking on ratio {}: {}, {}'.format(ratio, ratio[0], ratio[1]))
    x, y, l, h = size(window_name)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    pyautogui.moveTo(updated_x, updated_y)
    sleep(.5)
    mouse.click()  # pyautogui clicks do not work with league/directx
    sleep(wait)

def right_click(ratio, expected_window='', wait=1):
    # Window selection
    if expected_window != '' and not exists(expected_window):
        log.debug("Cannot click on {}, {} does not exist".format(ratio, expected_window))
        raise WindowNotFound
    elif expected_window != '':
        window_name = expected_window
    else:  # check if game is running and default to game otherwise set window to league client
        if exists(LEAGUE_GAME_CLIENT_WINNAME):
            window_name = LEAGUE_GAME_CLIENT_WINNAME
        elif exists(LEAGUE_CLIENT_WINNAME):
            window_name = LEAGUE_CLIENT_WINNAME
        else:
            log.debug("Cannot click on {}, no available window".format(ratio))
            return

    # Right Click
    x, y, l, h = size(window_name)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    pyautogui.moveTo(updated_x, updated_y)
    sleep(.5)
    mouse.right_click()  # pyautogui clicks do not work with league/directx
    sleep(wait)

# Keyboard
def attack_move_click(ratio, wait=1):
    if not exists(LEAGUE_GAME_CLIENT_WINNAME):
        log.debug("Cannot attack move when game is not running")
        raise WindowNotFound
    log.debug('Attack Moving on ratio {}: {}, {}'.format(ratio, ratio[0], ratio[1]))
    x, y, l, h = size(LEAGUE_GAME_CLIENT_WINNAME)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    pyautogui.moveTo(updated_x, updated_y)
    sleep(.5)
    keyboard.press('a')
    sleep(.1)
    mouse.click()
    sleep(.1)
    mouse.click()
    keyboard.release('a')
    sleep(wait)

def press(key, expected_window='', wait=1):
    if expected_window != '' and not exists(expected_window):
        log.debug("Cannot press {}, {} does not exist".format(key, expected_window))
        raise WindowNotFound
    log.debug("Pressing key: {}".format(key))
    keyboard.press_and_release(key)
    sleep(wait)

def write(keys, expected_window='', wait=1):
    if expected_window != '' and not exists(expected_window):
        log.debug("Cannot type {}, {} does not exist".format(keys, expected_window))
        raise WindowNotFound
    log.debug("Typewriting {}".format(keys))
    pyautogui.typewrite(keys)
    sleep(wait)

# Random
def seconds_to_min_sec(seconds):
    try:
        if isinstance(seconds, int) or isinstance(seconds, float):
            if len(str(int(seconds % 60))) == 1:
                return str(int(seconds / 60)) + ":0" + str(int(seconds % 60))
            else:
                return str(int(seconds / 60)) + ":" + str(int(seconds % 60))
        elif isinstance(seconds, str):
            seconds = float(seconds)
            if len(str(int(seconds % 60))) == 1:
                return str(int(seconds / 60)) + ":0" + str(int(seconds % 60))
            else:
                return str(int(seconds / 60)) + ":" + str(int(seconds % 60))
    except:
        return "XX:XX"