"""
Plays and through a single League of Legends match
"""

import logging
import random
from datetime import datetime, timedelta

from lolbot.bot.controller import *
from lolbot.bot.window import game_window_exists, WindowNotFound, GAME_WINDOW_NAME
import lolbot.lcu.game_api as api
import lolbot.common.proc as proc

log = logging.getLogger(__name__)

# Game Times
LOADING_SCREEN_TIME = 3
MINION_CLASH_TIME = 85
FIRST_TOWER_TIME = 630
MAX_GAME_TIME = 2400

# Click coordinates to move/aim
MINI_MAP_UNDER_TURRET = (0.8760, 0.8846)
MINI_MAP_CENTER_MID = (0.8981, 0.8674)
MINI_MAP_ENEMY_NEXUS = (0.9628, 0.7852)
ULT_DIRECTION = (0.7298, 0.2689)
CENTER_OF_SCREEN = (0.5, 0.5)

# Click coordinates to purchase items
AFK_OK_BUTTON = (0.4981, 0.4647)
SYSTEM_MENU_X_BUTTON = (0.7729, 0.2488)
SHOP_ITEM_BUTTONS = [(0.3216, 0.5036), (0.4084, 0.5096), (0.4943, 0.4928)]
SHOP_PURCHASE_ITEM_BUTTON = (0.7586, 0.6012)

MAX_ERRORS = 15


class GameError(Exception):
    """Indicates the game should be terminated"""
    pass


def play_game() -> None:
    """Plays a single game of League of Legends, takes actions based on game time"""
    game_errors = 0
    logged = False
    try:
        wait_for_game_window()
        wait_for_connection()
        while True:
            if api.is_dead():
                sleep(2)
                continue
            game_time = api.get_game_time()
            if game_time > MINION_CLASH_TIME and not logged:
                log.info("Destroying Enemy Nexus")
                logged = True
            if game_time < LOADING_SCREEN_TIME:
                loading_screen()
            elif game_time < MINION_CLASH_TIME:
                game_start()
            elif game_time < FIRST_TOWER_TIME:
                play(MINI_MAP_CENTER_MID, MINI_MAP_UNDER_TURRET, 20)
            elif game_time < MAX_GAME_TIME:
                play(MINI_MAP_ENEMY_NEXUS, MINI_MAP_CENTER_MID, 35)
            else:
                raise GameError("Game has exceeded the max time limit")
    except GameError as e:
        log.warning(str(e))
        proc.close_game()
        sleep(30)
    except api.GameAPIError as e:
        game_errors += 1
        if game_errors == MAX_ERRORS:
            log.error(f"Max Game Errors reached. {e}")
            proc.close_game()
            sleep(30)
    except (WindowNotFound, pyautogui.FailSafeException):
        log.info(f"Game Complete")


def wait_for_game_window() -> None:
    """Loop that waits for game window to open"""
    for i in range(120):
        sleep(1)
        if game_window_exists():
            log.debug("Game window open")
            left_click(CENTER_OF_SCREEN, GAME_WINDOW_NAME, 2)
            left_click(CENTER_OF_SCREEN, GAME_WINDOW_NAME)
            return
    raise GameError("Game window did not open")


def wait_for_connection() -> None:
    """Loop that waits for connection to local game server"""
    for i in range(120):
        if api.is_connected():
            return
        sleep(1)
    raise GameError("Game window opened but connection failed")


def loading_screen() -> None:
    """Loop that waits for loading screen to end"""
    log.info("Waiting for game to start")
    start = datetime.now()
    while api.get_game_time() < LOADING_SCREEN_TIME:
        sleep(2)
        if datetime.now() - start > timedelta(minutes=10):
            raise GameError("Loading screen max time limit exceeded")
    left_click(CENTER_OF_SCREEN, GAME_WINDOW_NAME, 2)


def game_start() -> None:
    """Buys starter items and waits for minions to clash (minions clash at 90 seconds)"""
    log.info("Buying items, heading mid, and waiting for minions")
    sleep(10)
    shop()
    keypress('y', GAME_WINDOW_NAME)  # lock screen
    upgrade_abilities()

    # Sit under turret till minions clash mid lane
    while api.get_game_time() < MINION_CLASH_TIME:
        right_click(MINI_MAP_UNDER_TURRET, GAME_WINDOW_NAME, 2)  # to prevent afk warning popup
        left_click(AFK_OK_BUTTON, GAME_WINDOW_NAME)


def play(attack: tuple, retreat: tuple, time_to_lane: int) -> None:
    """Buys items, levels up abilities, heads to lane, attacks, retreats, backs"""
    shop()
    upgrade_abilities()
    left_click(AFK_OK_BUTTON, GAME_WINDOW_NAME)

    # Walk to lane
    attack_move_click(attack, GAME_WINDOW_NAME)
    keypress('d', GAME_WINDOW_NAME)  # ghost
    sleep(time_to_lane)

    # Main attack move loop. This sequence attacks and then de-aggros to prevent them from dying 50 times.
    for i in range(7):
        attack_move_click(attack, GAME_WINDOW_NAME, 8)
        right_click(retreat, GAME_WINDOW_NAME, 2.5)

    # Ult and back
    keypress('f', GAME_WINDOW_NAME)
    attack_move_click(ULT_DIRECTION, GAME_WINDOW_NAME)
    keypress('r', GAME_WINDOW_NAME, 4)
    right_click(MINI_MAP_UNDER_TURRET, GAME_WINDOW_NAME, 6)
    keypress('b', GAME_WINDOW_NAME, 10)


def shop() -> None:
    """Opens the shop and attempts to purchase items via default shop hotkeys"""
    keypress('p', GAME_WINDOW_NAME, 1.5)  # open shop
    left_click(random.choice(SHOP_ITEM_BUTTONS), GAME_WINDOW_NAME, 1.5)
    left_click(SHOP_PURCHASE_ITEM_BUTTON, GAME_WINDOW_NAME, 1.5)
    keypress('esc', GAME_WINDOW_NAME, 1.5)
    left_click(SYSTEM_MENU_X_BUTTON, GAME_WINDOW_NAME, 1.5)


def upgrade_abilities() -> None:
    """Upgrades abilities and then rotates which ability will be upgraded first next time"""
    keypress('ctrl+r', GAME_WINDOW_NAME)
    upgrades = ['ctrl+q', 'ctrl+w', 'ctrl+e']
    random.shuffle(upgrades)
    for upgrade in upgrades:
        keypress(upgrade, GAME_WINDOW_NAME)
