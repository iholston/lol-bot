import logging
import pyautogui
import subprocess
import random
import shutil
import game
import account
import utils
import api
from time import sleep
from constants import *

log = logging.getLogger(__name__)

connection = api.Connection()

class ClientError(Exception):
    pass

class AccountLeveled(Exception):
    pass

def init():
    # Ensure game config file is correct
    log.info("Overwriting/creating game config")
    if os.path.exists(LEAGUE_GAME_CONFIG_PATH):
        shutil.copyfile(LOCAL_GAME_CONFIG_PATH, LEAGUE_GAME_CONFIG_PATH)
    else:
        shutil.copy2(LOCAL_GAME_CONFIG_PATH, LEAGUE_GAME_CONFIG_PATH)

    # Get account username and password
    username = account.get_username()
    password = account.get_password()

    # Start league
    log.info("Opening League of Legends")
    start_app(username, password)

    # Connect to API
    connection.init()
    sleep(3)

    # Client Update
    patcher()

# Main Control Loop
def loop():
    previous_phase = ''
    errno = 0

    while True:
        phase = get_phase()
        log.debug("Phase: {}".format(phase))

        if phase == previous_phase:
            errno += 1
            log.debug("Phase same as previous. Errno {}".format(errno))
            if errno == 15:
                log.warning("Transition error. Phase will not change.")
                raise ClientError
        else:
            errno = 0

        match phase:
            case 'None':
                create_default_lobby(GAME_LOBBY_ID)
            case 'Lobby':
                start_matchmaking(GAME_LOBBY_ID)
            case 'Matchmaking':
                queue()
            case 'ReadyCheck':
                accept_match()
            case 'ChampSelect':
                handle_game_lobby()
            case 'InProgress':
                game.play_game()
            case 'Reconnect':
                reconnect()
            case 'WaitingForStats':
                wait_for_stats()
            case 'PreEndOfGame':
                pre_end_of_game()
            case 'EndOfGame':
                end_of_game()
            case _:
                log.warning("Unknown phase: {}".format(phase))
                raise ClientError

        previous_phase = phase
        sleep(2)

# GAME FLOW FUNCS

def create_default_lobby(lobby_id):
    log.info("Creating lobby with lobby_id: {}".format(lobby_id))
    connection.request('post', '/lol-lobby/v2/lobby', data={'queueId': lobby_id})
    sleep(1.5)

def start_matchmaking(lobby_id):
    log.info("Starting queue for lobby_id: {}".format(lobby_id))
    r = connection.request('get', '/lol-lobby/v2/lobby')
    if r.json()['gameConfig']['queueId'] != lobby_id:
        create_default_lobby(lobby_id)
        sleep(1)
    connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
    sleep(1.5)

    # Check for dodge timer
    r = connection.request('get', '/lol-matchmaking/v1/search')
    if r.status_code == 200 and len(r.json()['errors']) != 0:
        dodge_timer = int(r.json()['errors'][0]['penaltyTimeRemaining'])
        log.info("Dodge Timer. Time Remaining: {}".format(utils.seconds_to_min_sec(dodge_timer)))
        sleep(dodge_timer)

def queue():
    log.info("In queue. Waiting for match.")
    while True:
        if get_phase() != 'Matchmaking':
            return
        sleep(1)

def accept_match():
    log.info("Accepting match")
    connection.request('post', '/lol-matchmaking/v1/ready-check/accept')

def handle_game_lobby():
    log.debug("Lobby State: INITIAL. Time Left in Lobby: 90s. Action: Initialize.")
    r = connection.request('get', '/lol-champ-select/v1/session')
    if r.status_code != 200:
        return
    cs = r.json()

    r2 = connection.request('get', '/lol-lobby-team-builder/champ-select/v1/pickable-champion-ids')
    if r2.status_code != 200:
        return
    f2p = r2.json()

    champ_index = 0
    f2p_index = 0
    requested = False
    while r.status_code == 200:
        lobby_state = cs['timer']['phase']
        lobby_time_left = int(float(cs['timer']['adjustedTimeLeftInPhase']) / 1000)

        # Find player action
        for action in cs['actions'][0]:  # There are 5 actions in the first action index, one for each player
            if action['actorCellId'] != cs['localPlayerCellId']:  # determine which action corresponds to bot
                continue

            # Check if champ is already locked in
            if not action['completed']:
                # Select Champ or Lock in champ that has already been selected
                if action['championId'] == 0:  # no champ selected, attempt to select a champ
                    log.info("Lobby State: {}. Time Left in Lobby: {}s. Action: Hovering champ.".format(lobby_state, lobby_time_left))

                    if champ_index < len(CHAMPS):
                        champion_id = CHAMPS[champ_index]
                        champ_index += 1
                    else:
                        champion_id = f2p[f2p_index]
                        f2p_index += 1

                    url = '/lol-champ-select/v1/session/actions/{}'.format(action['id'])
                    data = {'championId': champion_id}
                    connection.request('patch', url, data=data)
                else:  # champ selected, lock in
                    log.info("Lobby State: {}. Time Left in Lobby: {}s. Action: Locking in champ.".format(lobby_state, lobby_time_left))
                    url = '/lol-champ-select/v1/session/actions/{}'.format(action['id'])
                    data = {'championId': action['championId']}
                    connection.request('post', url + '/complete', data=data)

                    # Ask for mid
                    if not requested:
                        sleep(1)
                        chat(random.choice(ASK_4_MID_DIALOG), 'handle_game_lobby')
                        requested = True
            else:
                log.debug("Lobby State: {}. Time Left in Lobby: {}s. Action: Waiting".format(lobby_state, lobby_time_left))
            r = connection.request('get', '/lol-champ-select/v1/session')
            if r.status_code != 200:
                log.info('Lobby State: CLOSED. Time Left in Lobby: 0s. Action: Exit.')
                return
            cs = r.json()
            sleep(3)

def reconnect():
    for i in range(3):
        r = connection.request('post', '/lol-gameflow/v1/reconnect')
        if r.status_code == 204:
            return
        sleep(2)
    log.warning('Could not reconnect to game')

# Often times disconnects will happen after a game finishes. The client will indefinitely return
# the phase 'WaitingForStats'
def wait_for_stats():
    log.info("Waiting for stats.")
    for i in range(60):
        sleep(2)
        if get_phase() != 'WaitingForStats':
            return
    log.warning("Waiting for stats timeout.")
    raise ClientError

# Handles game client reopening, honoring teammates, clearing level up rewards and mission rewards
# This func should hopefully be updated to not include any clicking, but im not sure of any endpoints that clear
# the 'send email' popup or mission/level rewards
def pre_end_of_game():
    log.info("Honoring teammates and accepting rewards.")
    sleep(3)
    # occasionally the lcu-api will be ready before the actual client window appears
    # in this instance, the utils.click will throw an exception. just catch and wait
    try:
        utils.click(POPUP_SEND_EMAIL_X_RATIO, LEAGUE_CLIENT_WINNAME, 1)
        sleep(1)
        honor_player()
        sleep(2)
        utils.click(POPUP_SEND_EMAIL_X_RATIO, LEAGUE_CLIENT_WINNAME, 1)
        sleep(1)
        for i in range(3):
            utils.click(POST_GAME_SELECT_CHAMP_RATIO, LEAGUE_CLIENT_WINNAME, 1)
            utils.click(POST_GAME_OK_RATIO, LEAGUE_CLIENT_WINNAME, 1)
        utils.click(POPUP_SEND_EMAIL_X_RATIO, LEAGUE_CLIENT_WINNAME, 1)
    except:
        sleep(3)

# Checks account level before returning to lobby
def end_of_game():
    account_level = get_account_level()
    if account_level < ACCOUNT_MAX_LEVEL:
        log.info("ACCOUNT LEVEL: {}. Returning to game lobby.\n".format(account_level))
        connection.request('post', '/lol-lobby/v2/play-again')
        sleep(2)

        # Occasionally, posting to the play-again endpoint just does not work
        post = True
        for i in range(15):
            if get_phase() != 'EndOfGame':
                return
            if post:
                connection.request('post', '/lol-lobby/v2/play-again')
            else:
                create_default_lobby(GAME_LOBBY_ID)
            post = not post
            sleep(1)
        log.warning("Could not exit play-again screen.")
        raise ClientError
    else:
        log.info("SUCCESS: Account Leveled")
        raise AccountLeveled


# UTILITY FUNCS

def start_app(username, password):
    if is_league_running():
        log.info("League is already running...")
        return
    log.info("Starting League of Legends")
    subprocess.run([LEAGUE_PATH])
    time_out = 0
    prior_login = True
    waiting = False
    while True:
        if time_out == 30:
            log.error("Application failed to launch")
            raise ClientError
        if utils.exists(LEAGUE_CLIENT_WINNAME):
            if prior_login:
                log.info("League Client opened with Prior Login")
            else:
                log.info("Game Successfully Launched")
                output = subprocess.check_output(KILL_RIOT_CLIENT, shell=False)
                log.info(str(output, 'utf-8').rstrip())
            sleep(5)
            return
        if utils.exists(RIOT_CLIENT_WINNAME):
            if not waiting:
                log.info("Riot Client opened. Logging in")
                prior_login = False
                waiting = True
                time_out = 0

                # Login -> when login screen starts username field has focus
                pyautogui.getWindowsWithTitle(RIOT_CLIENT_WINNAME)
                sleep(3)
                pyautogui.typewrite(username)
                sleep(.5)
                pyautogui.press('tab')
                sleep(.5)
                pyautogui.typewrite(password)
                sleep(.5)
                pyautogui.press('enter')
                sleep(5)
            else:
                log.debug("Waiting for league to open...")
                sleep(1)
                pyautogui.press('enter')  # sometimes the riot client will force you to press 'play'
        sleep(1)
        time_out += 1

def patcher():
    log.info("Checking for Client Updates")
    r = connection.request('get', '/patcher/v1/products/league_of_legends/state')
    if r.status_code != 200:
        return
    logged = False
    while not r.json()['isUpToDate']:
        if not logged:
            log.info("Client is patching...")
            logged = True
        sleep(3)
        r = connection.request('get', '/patcher/v1/products/league_of_legends/state')
        log.debug('Status Code: {}, Percent Patched: {}%'.format(r.status_code, r.json()['percentPatched']))
        log.debug(r.json())
    log.info("Client is up to date!")

def close():
    log.info("Terminating league related processes.")
    os.system(KILL_LEAGUE)
    os.system(KILL_LEAGUE_CLIENT)
    os.system(KILL_RIOT_CLIENT)
    sleep(5)

def is_league_running():
    res = subprocess.check_output(["TASKLIST"], creationflags=0x08000000)
    output = str(res)
    for name in PROCESS_NAMES:
        if name in output:
            return True
    return False

def honor_player():
    for i in range(3):
        r = connection.request('get', '/lol-honor-v2/v1/ballot')
        if r.status_code == 200:
            players = r.json()['eligiblePlayers']
            index = random.randint(0, len(players)-1)
            connection.request('post', '/lol-honor-v2/v1/honor-player', data={"summonerId": players[index]['summonerId']})
            log.info("Honor Success: Player {}. Champ: {}. Summoner: {}. ID: {}".format(index+1, players[index]['championName'], players[index]['summonerName'], players[index]['summonerId']))
            return
        sleep(2)
    log.info('Honor Failure. Player -1, Champ: NULL. Summoner: NULL. ID: -1')
    connection.request('post', '/lol-honor-v2/v1/honor-player', data={"summonerId": 0})  # will clear honor screen

def chat(msg, calling_func_name=''):
    chat_id = ''
    r = connection.request('get', '/lol-chat/v1/conversations')
    if r.status_code != 200:
        if calling_func_name != '':
            log.warning("{} chat attempt failed. Could not reach endpoint".format(calling_func_name))
        else:
            log.warning("Could not reach endpoint")
        return

    for convo in r.json():
        if convo['gameName'] != '' and convo['gameTag'] != '':
            continue
        chat_id = convo['id']

    if chat_id == '':
        if calling_func_name != '':
            log.warning('{} chat attempt failed. Could not send message. Chat ID is Null'.format(calling_func_name))
        else:
            log.warning('Could not send message. Chat ID is Null')
        return

    data = {"body": msg}
    r = connection.request('post', '/lol-chat/v1/conversations/{}/messages'.format(chat_id), data=data)
    if r.status_code != 200:
        if calling_func_name != '':
            log.warning('{}, could not send message. HTTP STATUS: {} - {}'.format(calling_func_name, r.status_code, r.json()))
        else:
            log.warning('Could not send message. HTTP STATUS: {} - {}'.format(r.status_code, r.json()))
    else:
        if calling_func_name != '':
            log.debug("{}, message success. Msg: {}".format(calling_func_name, msg))
        else:
            log.debug("Message Success. Msg: {}".format(msg))

def get_phase():
    for i in range(15):
        r = connection.request('get', '/lol-gameflow/v1/gameflow-phase')
        if r.status_code == 200:
            return r.json()
        sleep(1)
    log.warning("Could not get phase.")
    raise ClientError

def get_account_level():
    for i in range(3):
        r = connection.request('get', '/lol-chat/v1/me')
        if r.status_code == 200:
            level = r.json()['lol']['level']
            return int(level)
        sleep(1)
    log.warning('Could not reach endpoint')
