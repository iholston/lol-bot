"""
This module provides functions to handle mouse clicks and movement on Windows.
On Windows, pyautogui mouse clicks do not work correctly. Need mouse package.
"""
from time import sleep

import mouse
import pyautogui

pyautogui.FAILSAFE = False

def left_click(wait=1):
    mouse.click()
    sleep(wait)

def right_click(wait=1):
    mouse.right_click()
    sleep(wait)

def move(coords: tuple, wait=.3):
    pyautogui.moveTo(coords)
    sleep(wait)

def move_and_click(coords: tuple, wait=1):
    pyautogui.moveTo(coords)
    sleep(.3)
    mouse.click()
    sleep(wait)
