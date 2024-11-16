"""
This module provides functions to handle mouse clicks and movement on macOS.

On macOS, pyautogui functions as expected.
"""
from time import sleep

import pyautogui

def left_click(wait = 1):
    pyautogui.leftClick()
    sleep(wait)

def right_click(wait = 1):
    pyautogui.rightClick()
    sleep(wait)

def move(coords: tuple, wait = .3):
    pyautogui.moveTo(coords)
    sleep(wait)

def move_and_click(coords: tuple, wait = 1):
    pyautogui.moveTo(coords)
    sleep(.3)
    pyautogui.leftClick()
    sleep(wait)