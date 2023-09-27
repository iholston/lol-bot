"""
Plays and monitors the state of a single League of Legends match
"""

import logging
import inspect
import random
import pyautogui
import requests
import utils
from enum import Enum
from datetime import datetime, timedelta
from time import sleep
from constants import *


class GameState(Enum):
    LOADING_SCREEN = 0  # 0 sec -> 3 sec
    PRE_MINIONS = 1     # 3 sec -> 90 sec
    EARLY_GAME = 2      # 90 sec -> constants.EARLY_GAME_END_TIME
    LATE_GAME = 3       # constants.EARLY_GAME_END_TIME -> end of game


class GameError(Exception):
    """Indicates the game should be terminated"""
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return self.msg


class Game:
    """Game class that handles the tasks needed to play/win a bot game of League of Legends"""
    
    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.connection_errors = 0
        self.game_data = None
        self.game_time = None
        self.formatted_game_time = None
        self.game_state = None
        self.screen_locked = False
        self.in_lane = False
        self.is_dead = False
        self.inventory = set()
        self.build_order = self.create_build_order()
        self.ability_upgrades = ['ctrl+r', 'ctrl+q', 'ctrl+w', 'ctrl+e']
        self.log.info("Game player initialized")

    def play_game(self) -> None:
        """Plays a single game of League of Legends, takes actions based on game time"""
        try:
            self.wait_for_game_window()
            self.wait_for_connection()
            while True:
                self.update_state()
                match self.game_state:
                    case GameState.LOADING_SCREEN:
                        self.loading_screen()
                    case GameState.PRE_MINIONS:
                        self.game_start()
                    case GameState.EARLY_GAME:
                        self.play(GAME_MINI_MAP_CENTER_MID, GAME_MINI_MAP_UNDER_TURRET, 20)
                    case GameState.LATE_GAME:
                        self.play(GAME_MINI_MAP_ENEMY_NEXUS, GAME_MINI_MAP_CENTER_MID, 35)
        except GameError as e:
            self.log.warning(e.__str__())
            utils.close_game()
        except (utils.WindowNotFound, pyautogui.FailSafeException):
            self.log.info("Game Complete")

    def wait_for_game_window(self) -> None:
        """Loop that waits for game window to open"""
        self.log.debug("Waiting for game window to open")
        for i in range(120):
            sleep(1)
            if utils.exists(LEAGUE_GAME_CLIENT_WINNAME):
                self.log.debug("Game window open")
                return
        raise GameError("Game window did not open")

    def wait_for_connection(self) -> None:
        """Loop that waits for connection to local game server"""
        self.log.debug("Connecting to game server...")
        for i in range(120):
            if self.update_state():
                self.log.debug("Connected to game server")
                return
        raise GameError("Game window opened but connection failed")

    def loading_screen(self) -> None:
        """Loop that waits for loading screen to end"""
        self.log.info("In loading screen. Waiting for game to start")
        start = datetime.now()
        while self.game_time < 3:
            if datetime.now() - start > timedelta(minutes=10):
                raise GameError("Loading Screen max time limit exceeded")
            self.update_state(postpone_update=2)
        utils.click(GAME_CENTER_OF_SCREEN, LEAGUE_GAME_CLIENT_WINNAME, 2)
        utils.click(GAME_CENTER_OF_SCREEN, LEAGUE_GAME_CLIENT_WINNAME)

    def game_start(self) -> None:
        """Buys starter items and waits for minions to clash (minions clash at 90 seconds)"""
        self.log.info("Game start. Buying starter items and heading mid")
        sleep(10)
        self.buy_item()
        self.lock_screen()
        self.upgrade_abilities()
        while self.game_state == GameState.PRE_MINIONS:
            utils.right_click(GAME_MINI_MAP_UNDER_TURRET, LEAGUE_GAME_CLIENT_WINNAME, 2)  # to prevent afk warning popup
            utils.click(GAME_AFK_OK_RATIO, LEAGUE_GAME_CLIENT_WINNAME)
            self.update_state()
        self.in_lane = True

    def play(self, attack_position: tuple, retreat_position: tuple, time_to_lane: int) -> None:
        """A set of player actions. Buys items, levels up abilites, heads to lane, attacks, then retreats"""
        self.log.debug("Main player loop. GameState: {}".format(self.game_state))
        self.buy_item()
        self.lock_screen()
        self.upgrade_abilities()
        while self.is_dead:
            self.update_state()
        utils.click(GAME_AFK_OK_RATIO, LEAGUE_GAME_CLIENT_WINNAME)
        if not self.in_lane:
            utils.attack_move_click(attack_position)
            utils.press('d', LEAGUE_GAME_CLIENT_WINNAME)  # ghost
            sleep(time_to_lane)
            self.in_lane = True

        # Main attack move loop. This sequence attacks and then de-aggros to prevent them from dying 50 times.
        for i in range(7):
            utils.attack_move_click(attack_position, 9)
            utils.right_click(retreat_position, LEAGUE_GAME_CLIENT_WINNAME, 2)

        # Ult and back
        utils.press('f', LEAGUE_GAME_CLIENT_WINNAME)
        utils.attack_move_click(GAME_ULT_RATIO)
        utils.press('r', LEAGUE_GAME_CLIENT_WINNAME, 4)
        utils.right_click(GAME_MINI_MAP_UNDER_TURRET, LEAGUE_GAME_CLIENT_WINNAME, 6)
        utils.press('b', LEAGUE_GAME_CLIENT_WINNAME, 10)
        self.in_lane = False

    def buy_item(self) -> None:
        """
        Opens the shop and attempts to purchase items

        p - opens the shop
        ctrl+l - focuses search bar
        esc - closes the shop
        We use esc to close the shop instead of p or clicking on the gold because if the shop wasn't
        actually opened by p click, the system menu will appear, and we can click the X button on it
        consistently since it always opens in the same spot (unlike the shop)
        """

        self.log.debug("Attempting to purchase an item from build order")
        utils.press('p', LEAGUE_GAME_CLIENT_WINNAME, 1.5)
        utils.press('ctrl+l', LEAGUE_GAME_CLIENT_WINNAME, 1.5)
        utils.write(self.build_order[0], LEAGUE_GAME_CLIENT_WINNAME, 1.5)
        utils.press('enter', LEAGUE_GAME_CLIENT_WINNAME, 1.5)
        self.update_state()
        if self.build_order[0] in self.inventory:
            self.log.debug("Successfully purchased: {}".format(self.build_order[0]))
            self.build_order.remove(self.build_order[0])
        utils.press('esc', LEAGUE_GAME_CLIENT_WINNAME, 1.5)
        utils.click(GAME_SYSTEM_MENU_X, LEAGUE_GAME_CLIENT_WINNAME, 1.5)

    def lock_screen(self) -> None:
        """Locks screen on champion"""
        if not self.screen_locked:
            self.log.debug("Locking screen")
            utils.press('y', LEAGUE_GAME_CLIENT_WINNAME)
            self.screen_locked = True

    def upgrade_abilities(self) -> None:
        """Upgrades abilities and then rotates which ability will be upgraded first next time"""
        self.log.debug("Upgrading abilities. Second Ability: {}".format(self.ability_upgrades[1]))
        for upgrade in self.ability_upgrades:
            utils.press(upgrade, LEAGUE_GAME_CLIENT_WINNAME)
        self.ability_upgrades = ([self.ability_upgrades[0]] + [self.ability_upgrades[-1]] + self.ability_upgrades[1:-1])  # r is always first

    def create_build_order(self) -> list[str]:
        """
        Randomly generates a build order

        Boots come after LEGENDARY_ITEMS because items are bought in order and slightly magical
        boots will prevent buying any items for a long time
        """
        build = [random.choice(STARTER_ITEMS)]
        build.extend(random.choice(LEGENDARY_ITEMS))
        build.append(random.choice(BOOTS))
        build.extend(random.choice(MYTHIC_ITEMS))
        self.log.debug("Build order created: {}".format(build))
        return build

    def update_state(self, postpone_update=1) -> bool:
        """Gets game data from local game server and updates game state"""
        self.log.debug("Updating state. Caller: {}".format(inspect.stack()[1][3]))
        sleep(postpone_update)
        try:
            response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', timeout=10, verify=False)
        except requests.ConnectionError:
            self.log.debug("Connection error. Could not get game data")
            self.connection_errors += 1
            if not utils.exists(LEAGUE_GAME_CLIENT_WINNAME):
                raise utils.WindowNotFound
            if self.connection_errors == 15:
                raise GameError("Could not connect to game")
            return False
        if response.status_code != 200:
            self.log.debug("Connection error. Response status code: {}".format(response.status_code))
            self.connection_errors += 1
            if not utils.exists(LEAGUE_GAME_CLIENT_WINNAME):
                raise utils.WindowNotFound
            if self.connection_errors == 15:
                raise GameError("Could not connect to game")
            return False

        self.game_data = response.json()
        for player in self.game_data['allPlayers']:
            if player['summonerName'] == self.game_data['activePlayer']['summonerName']:
                self.is_dead = bool(player['isDead'])
                for item in player['items']:
                    self.inventory.add(item['displayName'])
        self.game_time = int(self.game_data['gameData']['gameTime'])
        self.formatted_game_time = utils.seconds_to_min_sec(self.game_time)
        if self.game_time < 3:
            self.game_state = GameState.LOADING_SCREEN
        elif self.game_time < 85:
            self.game_state = GameState.PRE_MINIONS
        elif self.game_time < EARLY_GAME_END_TIME:
            if self.game_state != GameState.EARLY_GAME:
                self.log.info("Early Game. Pushing center mid. Game Time: {}".format(self.formatted_game_time))
            self.game_state = GameState.EARLY_GAME
        elif self.game_time < MAX_GAME_TIME:
            if self.game_state != GameState.LATE_GAME:
                self.log.info("Mid Game. Pushing enemy nexus. Game Time: {}".format(self.formatted_game_time))
            self.game_state = GameState.LATE_GAME
        else:
            raise GameError("Game has exceeded the max time limit")
        self.connection_errors = 0
        self.log.debug("State Updated. Game Time: {}, Game State: {}, IsDead: {}, Inventory: {}".format(self.game_time, self.game_state, self.is_dead, self.inventory))
        return True
