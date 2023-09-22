import logging
import random
import pyautogui
import requests
import utils
from enum import Enum
from datetime import datetime, timedelta
from time import sleep
from constants import *

class GameState(Enum):
    LOADING_SCREEN = 0
    PRE_MINIONS = 1
    EARLY_GAME = 2
    LATE_GAME = 3

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
        self.game_data = {}
        self.game_time = -1
        self.formatted_game_time = ''
        self.game_state = None

    def play_game(self) -> None:
        """Plays a single game of League of Legends, takes action based on game time"""
        try:
            self.wait_for_game_window()
            self.wait_for_game_connection()
            while True:
                sleep(1)
                if self.update_state():
                    match self.game_state:
                        case GameState.LOADING_SCREEN:
                            self.loading_screen()
                        case GameState.PRE_MINIONS:
                            self.game_start()
                        case GameState.EARLY_GAME:
                            self.early_game()
                        case GameState.LATE_GAME:
                            self.late_game()
        except GameError as e:
            self.log.warning(e.__str__())
            utils.close_game()
        except (utils.WindowNotFound, pyautogui.FailSafeException):
            self.log.info("Game Complete. Game Length: {}".format(self.formatted_game_time))

    @staticmethod
    def wait_for_game_window() -> None:
        """Loop that waits for game window to open"""
        for i in range(120):
            sleep(1)
            if utils.exists(LEAGUE_GAME_CLIENT_WINNAME):
                return
        raise GameError("Game window did not open")

    def wait_for_game_connection(self) -> None:
        """Loop that waits for connection to local game server"""
        for i in range(120):
            sleep(1)
            if self.update_state():
                return
        raise GameError("Game window opened but connection failed")

    def loading_screen(self) -> None:
        """Loop that waits for loading screen to end"""
        start = datetime.now()
        while self.game_time < 3:
            if datetime.now() - start > timedelta(minutes=10):
                raise GameError("Loading Screen max time limit exceeded")
            else:
                self.update_state()
                sleep(2)

    def game_start(self):
        """Buys starter items and waits for minions to clash (minions clash at 90 seconds)"""
        self.buy_items(GAME_BUY_STARTER_ITEM_RATIO)
        utils.press()

    def early_game(self):
        pass

    def late_game(self):
        pass

    def buy_items(self, ratio):
        pass

    def update_state(self) -> bool:
        """Gets game data from local game server and updates game state"""
        try:
            response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', timeout=10, verify=False)
        except requests.ConnectionError:
            return False
        if response.status_code != 200:
            return False

        self.game_data = response.json()
        self.game_time = int(self.game_data['gameData']['gameTime'])
        self.formatted_game_time = utils.seconds_to_min_sec(self.game_time)
        if self.game_time < 3:
            self.game_state = GameState.LOADING_SCREEN
        elif self.game_time < 85:
            self.game_state = GameState.PRE_MINIONS
        elif self.game_time < EARLY_GAME_END_TIME:
            self.game_state = GameState.EARLY_GAME
        elif self.game_time < MAX_GAME_TIME:
            self.game_state = GameState.LATE_GAME
        else:
            raise GameError("Game has exceeded the max time limit")
        self.log.info("Game State: {}, Game Time: {}".format(self.game_state, self.formatted_game_time))
        return True


