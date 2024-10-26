"""
Module that handles clicks and key presses.
"""

from time import sleep

import keyboard
import mouse  # pyautogui clicks do not work with league/directx
import pyautogui

from lolbot.bot.window import *


def keypress(key: str, window: str = '', wait: float = 1) -> None:
    """Sends a keypress to a window"""
    if window != '' and not window_exists(window):
        raise WindowNotFound
    keyboard.press_and_release(key)
    sleep(wait)


def write(keys: str, window: str = '', wait: float = 1) -> None:
    """Sends a string of key presses to a window"""
    if window != '' and not window_exists(window):
        raise WindowNotFound
    pyautogui.write(keys, interval=0.11)
    sleep(wait)


def left_click(ratio: tuple, window: str, wait: float = 1) -> None:
    """Makes a click in an open window"""
    _move_to_window_coords(ratio, window)
    mouse.click()
    sleep(wait)


def right_click(ratio: tuple, window: str, wait: float = 1) -> None:
    """Makes a right click in an open window"""
    _move_to_window_coords(ratio, window)
    mouse.right_click()
    sleep(wait)


def attack_move_click(ratio: tuple, window: str, wait: float = 1) -> None:
    """Attack move clicks in an open window"""
    _move_to_window_coords(ratio, window)
    keyboard.press('a')
    sleep(.1)
    mouse.click()
    sleep(.1)
    mouse.click()
    keyboard.release('a')
    sleep(wait)


def _move_to_window_coords(ratio: tuple, window: str):
    if not window_exists(window):
        raise WindowNotFound
    x, y, l, h = get_window_size(window)
    updated_x = ((l - x) * ratio[0]) + x
    updated_y = ((h - y) * ratio[1]) + y
    pyautogui.moveTo(updated_x, updated_y)
    sleep(.5)
