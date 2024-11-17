"""
Game logic that plays and through a single League of Legends match.
"""

import logging
import random
from time import sleep
from datetime import datetime, timedelta

from lolbot.lcu.game_server import GameServer, GameServerError
from lolbot.system import mouse, keys, window, cmd

log = logging.getLogger(__name__)

# Game Times
LOADING_SCREEN_TIME = 3
MINION_CLASH_TIME = 85
FIRST_TOWER_TIME = 1500
MAX_GAME_TIME = 3000

# Click coordinates to move/aim
MINI_MAP_UNDER_TURRET = (0.89, 0.89)
MINI_MAP_CENTER_MID = (0.91, 0.87)
MINI_MAP_ENEMY_NEXUS = (0.9628, 0.7852)
ULT_DIRECTION = (0.7298, 0.2689)
CENTER_OF_SCREEN = (0.5, 0.5)

# Click coordinates to purchase items
AFK_OK_BUTTON = (0.4981, 0.4647)
SYSTEM_MENU_X_BUTTON = (0.7729, 0.2488)
SHOP_ITEM_BUTTONS = [(0.3216, 0.5036), (0.4084, 0.5096), (0.4943, 0.4928)]
SHOP_PURCHASE_ITEM_BUTTON = (0.7586, 0.6012)

MAX_SERVER_ERRORS = 15


class GameError(Exception):
    """Indicates the game should be terminated"""
    pass


def play_game() -> None:
    """Plays a single game of League of Legends, takes actions based on game time"""
    game_server = GameServer()
    try:
        wait_for_game_window()
        wait_for_connection(game_server)
        game_loop(game_server)
    except GameError as e:
        log.warning(e)
        cmd.run(cmd.CLOSE_GAME)
        sleep(30)
    except window.WindowNotFound:
        log.info(f"Game Complete")


def wait_for_game_window() -> None:
    """Loop that waits for game window to open"""
    for i in range(120):
        sleep(1)
        if window.check_window_exists(window.GAME_WINDOW):
            log.debug("Game window open")
            left_click(CENTER_OF_SCREEN)
            left_click(CENTER_OF_SCREEN)
            return
    raise GameError("Game window did not open")


def wait_for_connection(game_server: GameServer) -> None:
    for i in range(120):
        if game_server.is_running():
            return
        sleep(1)
    raise GameError("Game window opened but connection failed")


def game_loop(game_server: GameServer) -> None:
    server_errors = 0
    try:
        while True:
            # Don't start new sequence when dead
            if game_server.summoner_is_dead():
                sleep(2)
                continue

            # Take action based on game time
            game_time = game_server.get_game_time()
            if game_time < LOADING_SCREEN_TIME:
                loading_screen(game_server)
            elif game_time < MINION_CLASH_TIME:
                game_start(game_server)
            elif game_time < FIRST_TOWER_TIME:
                play(game_server, MINI_MAP_CENTER_MID, MINI_MAP_UNDER_TURRET, 20)
            elif game_time < MAX_GAME_TIME:
                play(game_server, MINI_MAP_ENEMY_NEXUS, MINI_MAP_CENTER_MID, 35)
            else:
                raise GameError("Game has exceeded the max time limit")
    except GameServerError as e:
        server_errors += 1
        if server_errors == MAX_SERVER_ERRORS:
            raise GameError(f"Max Server Errors reached: {e}")


def loading_screen(game_server: GameServer) -> None:
    log.info("Waiting for game to start")
    start = datetime.now()
    while game_server.get_game_time() < LOADING_SCREEN_TIME:
        sleep(2)
        if datetime.now() - start > timedelta(minutes=10):
            raise GameError("Loading screen max time limit exceeded")
    left_click(CENTER_OF_SCREEN)


def game_start(game_server: GameServer) -> None:
    """Buys starter items and waits for minions to clash (minions clash at 90 seconds)"""
    log.info("Buying items, heading mid, and waiting for minions")
    sleep(10)
    shop()
    keypress('y')  # lock screen
    upgrade_abilities()

    # Sit under turret till minions clash mid lane
    while game_server.get_game_time() < MINION_CLASH_TIME:
        right_click(MINI_MAP_UNDER_TURRET)  # to prevent afk warning popup
        left_click(AFK_OK_BUTTON)


def play(game_server: GameServer, attack_position: tuple, retreat: tuple, time_to_lane: int) -> None:
    """Buys items, levels up abilities, heads to lane, attacks, retreats, backs"""
    shop()
    upgrade_abilities()
    left_click(AFK_OK_BUTTON)

    # Walk to lane
    attack_click(attack_position)
    keypress('d')  # ghost
    sleep(time_to_lane)

    # Main attack move loop. This sequence attacks and then de-aggros to prevent them from dying 50 times.
    for i in range(8):
        if game_server.get_summoner_health() < .5:
            right_click(retreat)
            sleep(4)
            break
        attack_click(attack_position)
        sleep(5)
        right_click(retreat)
        sleep(3)

    # Ult and back
    keypress('f')
    attack_click(ULT_DIRECTION)
    keypress('r')
    right_click(MINI_MAP_UNDER_TURRET)
    sleep(6)
    keypress('b')
    sleep(10)


def shop() -> None:
    """Opens the shop and attempts to purchase items via default shop hotkeys"""
    keypress('p')  # open shop
    left_click(random.choice(SHOP_ITEM_BUTTONS))
    left_click(SHOP_PURCHASE_ITEM_BUTTON)
    keypress('esc')
    left_click(SYSTEM_MENU_X_BUTTON)


def upgrade_abilities() -> None:
    window.check_window_exists(window.GAME_WINDOW)
    keys.press_and_release('ctrl+r')
    upgrades = ['ctrl+q', 'ctrl+w', 'ctrl+e']
    random.shuffle(upgrades)
    for upgrade in upgrades:
        keys.press_and_release(upgrade)


def left_click(ratio: tuple) -> None:
    coords = window.convert_ratio(ratio, window.GAME_WINDOW)
    mouse.move(coords)
    mouse.left_click()
    sleep(1)


def right_click(ratio: tuple) -> None:
    coords = window.convert_ratio(ratio, window.GAME_WINDOW)
    mouse.move(coords)
    mouse.right_click()
    sleep(1)


def attack_click(ratio: tuple) -> None:
    coords = window.convert_ratio(ratio, window.GAME_WINDOW)
    mouse.move(coords)
    keys.key_down('a')
    sleep(.1)
    mouse.left_click()
    sleep(.1)
    mouse.left_click()
    keys.key_up('a')
    sleep(1)


def keypress(key: str) -> None:
    window.check_window_exists(window.GAME_WINDOW)
    keys.press_and_release(key)
    sleep(1)
