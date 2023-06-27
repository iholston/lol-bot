import logging
import random
import pyautogui
import requests
import utils
import subprocess
from datetime import datetime, timedelta
from time import sleep
from constants import *

log = logging.getLogger(__name__)

def play_game():
    log.info("Game State: NONE. Game Time: NULL. Action: Initializing...")

    connection_err = 0
    while not utils.exists(LEAGUE_GAME_CLIENT_WINNAME):
        if connection_err == 60:
            log.warning("Could not connect to game.")
            close_game()
            sleep(10)
            return
        sleep(2)
        if get_game_data() == {}:
            connection_err += 1

    data = get_game_data()
    connection_err = 0
    while len(data) == 0:
        if connection_err == 120:
            log.warning("Window open but cannot connect to game.")
            close_game()
            sleep(10)
            return
        sleep(2)
        data = get_game_data()
        connection_err += 1

    game_time = int(data['gameData']['gameTime'])
    loading_screen_logged = False
    loading_screen_time = datetime.now()
    in_lane = False
    initial_items = False
    screen_locked = False
    logged_early_game = False
    logged_mid_late_game = False
    try:
        sleep(1.5)
        utils.click(GAME_CENTER_OF_SCREEN, LEAGUE_GAME_CLIENT_WINNAME)
    except pyautogui.FailSafeException:
        log.warning("Error attempting to click center of screen")

    # Main Loop
    while True:
        formatted_game_time = utils.seconds_to_min_sec(game_time)

        # Connection errors can cause league games to never exit
        if game_time > 2400:
            log.warning("Game exceeded max time limit. Exiting.")
            try:
                close_game()
                sleep(10)
            except:
                pass
            return

        # All clicks and button presses are expecting the game window, if it does not exist the game is over
        try:
            # Loading Screen
            if game_time < 3:
                if not loading_screen_logged:
                    log.info("Game State: LOADING SCREEN. Game Time: NULL. Action: Wait.")
                    loading_screen_logged = True
                if datetime.now() - loading_screen_time > timedelta(minutes=10):
                    log.warning("Load Screen exceeded max time limit. Exiting.")
                    try:
                        output = subprocess.check_output(KILL_LEAGUE, shell=False)
                        log.info(str(output, 'utf-8').rstrip())
                    except:
                        pass
                    return
                sleep(2)

            # Game Start
            elif game_time < 85:  # Minions clash together at 90 seconds
                # Open shop and buy starter items
                if not initial_items:
                    log.info("Game State: INITIAL FOUNTAIN. Game Time: {}. Action: Buying starter items and heading to mid lane.".format(formatted_game_time))
                    sleep(2)
                    utils.press('p', LEAGUE_GAME_CLIENT_WINNAME)
                    sleep(1)
                    utils.click(GAME_ALL_ITEMS_RATIO, LEAGUE_GAME_CLIENT_WINNAME, 1)
                    for _ in range(2):  # just in case tbh, don't need for loop
                        scale = tuple([random.randint(1, STARTER_ITEMS_TO_BUY) * x for x in GAME_BUY_ITEM_RATIO_INCREASE])  # there are less starter items
                        positions = tuple(sum(x) for x in zip(GAME_BUY_STARTER_ITEM_RATIO, scale))  # add tuple to default item position ratio https://stackoverflow.com/questions/1169725/adding-values-from-tuples-of-same-length
                        utils.click(positions, LEAGUE_GAME_CLIENT_WINNAME, 1)
                        utils.click(GAME_BUY_PURCHASE_RATIO, LEAGUE_GAME_CLIENT_WINNAME, 1)
                    utils.press('p', LEAGUE_GAME_CLIENT_WINNAME)
                    utils.press('y')
                    screen_locked = True
                    initial_items = True

                # Head to mid lane turret and wait for minions
                utils.press('ctrl+q')
                utils.attack_move_click(GAME_MINI_MAP_UNDER_TURRET)
                in_lane = True
                sleep(5)

            # Game Running
            else:
                if game_time < EARLY_GAME_END_TIME:  # Early Game, don't run it down mid
                    game_state = 'EARLY GAME'
                    primary_location = GAME_MINI_MAP_UNDER_TURRET
                    backup_location = GAME_MINI_MAP_UNDER_TURRET
                    to_lane_time = 20
                    if not logged_early_game:
                        log.info("Game State: {}. Game Time: {}. Action: {} Rotation.".format(game_state, formatted_game_time, game_state))
                        logged_early_game = True
                else:
                    game_state = 'MID/LATE GAME'
                    primary_location = GAME_MINI_MAP_ENEMY_NEXUS
                    backup_location = GAME_MINI_MAP_CENTER_MID
                    to_lane_time = 35
                    if not logged_mid_late_game:
                        log.info("Game State: {}. Game Time: {}. Action: {} Rotation.".format(game_state, formatted_game_time, game_state))
                        logged_mid_late_game = True

                if not screen_locked:
                    utils.press('y', LEAGUE_GAME_CLIENT_WINNAME)
                    screen_locked = True

                log.debug("Game State: {}. Game Time: {}. Action: {} Rotation.".format(game_state, formatted_game_time, game_state))

                # Open shop and buy items
                utils.press('p', LEAGUE_GAME_CLIENT_WINNAME)
                for _ in range(ITEMS_TO_BUY):
                    scale = tuple([random.randint(1, ITEMS_TO_BUY) * x for x in
                                   GAME_BUY_ITEM_RATIO_INCREASE])  # multiply tuple by scaler https://stackoverflow.com/questions/1781970/multiplying-a-tuple-by-a-scalar
                    positions = tuple(sum(x) for x in zip(GAME_BUY_EPIC_ITEM_RATIO,
                                                          scale))  # add tuple to default item position ratio https://stackoverflow.com/questions/1169725/adding-values-from-tuples-of-same-length
                    utils.click(positions, LEAGUE_GAME_CLIENT_WINNAME, .5)
                    utils.click(GAME_BUY_PURCHASE_RATIO, LEAGUE_GAME_CLIENT_WINNAME, .5)
                utils.press('p', LEAGUE_GAME_CLIENT_WINNAME)

                # Go to lane

                # Upgrade abilities
                utils.press('ctrl+r', LEAGUE_GAME_CLIENT_WINNAME)
                utils.press('ctrl+q', LEAGUE_GAME_CLIENT_WINNAME)
                utils.press('ctrl+w', LEAGUE_GAME_CLIENT_WINNAME)
                utils.press('ctrl+e', LEAGUE_GAME_CLIENT_WINNAME)
                if not in_lane:
                    utils.attack_move_click(
                        primary_location)  # if you right utils.click they will walk under turret and die instantly
                    utils.press('d', LEAGUE_GAME_CLIENT_WINNAME)  # ghost
                    sleep(to_lane_time)
                    in_lane = False

                # Main attack move loop. This sequence de-aggros them and prevents them from dying 50 times. In the early game they are actually positive most games
                loops = 7
                for i in range(loops):
                    # Attack
                    utils.attack_move_click(GAME_MINI_MAP_ENEMY_NEXUS)
                    sleep(8)
                    # De-aggro or Ult and Back
                    if i != loops - 1:
                        utils.right_click(backup_location, LEAGUE_GAME_CLIENT_WINNAME)
                        sleep(1)
                    else:
                        # Ult
                        utils.press('f', LEAGUE_GAME_CLIENT_WINNAME)
                        utils.attack_move_click(GAME_ULT_RATIO)
                        utils.press('r', LEAGUE_GAME_CLIENT_WINNAME)
                        sleep(3)
                        utils.right_click(GAME_MINI_MAP_UNDER_TURRET, LEAGUE_GAME_CLIENT_WINNAME)
                        sleep(5)
                        utils.press('b', LEAGUE_GAME_CLIENT_WINNAME)
                        sleep(9)
            data = get_game_data()
            if len(data) != 0:
                game_time = int(data['gameData']['gameTime'])

        except utils.WindowNotFound:
            log.info("Game State: COMPLETE. Game Length: {}. Action: Exit.".format(utils.seconds_to_min_sec(game_time)))
            return
        except pyautogui.FailSafeException:  # unlikely but possible
            log.warning("FailSafeException. Game State: Considered COMPLETE. Game Length: {}. Action: Exit.".format(utils.seconds_to_min_sec(game_time)))
            return

def get_game_data():
    try:
        request_game_data = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
        if request_game_data.status_code == 200:
            return request_game_data.json()
        else:
            return {}
    except Exception as e:
        log.warning("get_game_data error {}".format(e))
        return {}

def close_game():
    log.warning("Terminating Game.")
    os.system(KILL_LEAGUE)
    sleep(5)