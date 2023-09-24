"""
Builds ratios for the bot to click on in the League Client or a League of Legends game window

Run and simply hover your mouse wherever you want to get a ratio in the
window that you pass to the functions. check the ratio after with the
check_ratio func
"""

import pyautogui
from time import sleep
from win32gui import FindWindow, GetWindowRect

client_title = "League of Legends"  # if you want to create a ratio for the League Client use this title
game_client_title = "League of Legends (TM) Client"  # if you want to create a ratio for the League of Legends game window use this title

def size(window_title) -> tuple:
    """Helper function to calculate ratio"""
    window_handle = FindWindow(None, window_title)
    window_rect = GetWindowRect(window_handle)
    return window_rect[0], window_rect[1], window_rect[2], window_rect[3]

def print_ratios(window_title) -> None:
    """This function will print out the ratio as you hover your mouse over the window"""
    while True:
        sleep(1)
        p = pyautogui.position()
        x1, y1, x2, y2 = size(window_title)
        rx = (p[0] - x1) / (x2 - x1)
        ry = (p[1] - y1) / (y2 - y1)
        print("({}, {})".format(round(rx, 4), round(ry, 4)))

def check_ratio(ratio, window_title) -> None:
    """This function will move the mouse to the ratio in the same way the lol-bot would"""
    x, y, l, h = size(window_title)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    pyautogui.moveTo(updated_x, updated_y, duration=.5)

# check_ratio((0.8712, 0.9752), client_title)
print_ratios(client_title)
