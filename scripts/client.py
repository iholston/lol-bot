"""
Controls the League Client and continually starts League of Legends games
"""

import logging
import random
import traceback
import inspect
import pyautogui
import utils
import api
import launcher
import account
from time import sleep
from datetime import datetime, timedelta
from constants import *
from game import Game
from handler import MultiProcessLogHandler


class ClientError(Exception):
    """Indicates the League Client instance should be restarted"""
    def __init__(self, msg: str = ''):
        self.msg = msg

    def __str__(self):
        return self.msg


class Client:
    """Client class that handles the League Client and all tasks needed to start a new game"""

    def __init__(self, message_queue) -> None:
        self.connection = api.Connection()
        self.launcher = launcher.Launcher()
        self.log = logging.getLogger(__name__)
        self.handler = MultiProcessLogHandler(message_queue)
        self.username = ""
        self.password = ""
        self.account_level = 0
        self.phase = ""
        self.prev_phase = None
        self.client_errors = 0
        self.phase_errors = 0
        self.handler.set_logs()
        utils.print_ascii()
        self.account_loop()

    def account_loop(self) -> None:
        """Main loop, gets an account, launches league, levels the account, and repeats"""
        while True:
            try:
                self.launcher.launch_league(account.get_username(), account.get_password())
                self.leveling_loop()
                account.set_account_as_leveled()
                utils.close_processes()
                self.client_errors = 0
            except ClientError as ce:
                self.log.error(ce.__str__())
                self.client_errors += 1
                if self.client_errors == MAX_CLIENT_ERRORS:
                    raise ClientError("Max errors reached.Exiting")
                utils.close_processes()
            except launcher.LauncherError as le:
                pyautogui.alert(le)
                self.log.error(le.__str__())
                self.log.error(traceback.print_exc())
                return
            except Exception as e:
                pyautogui.alert(e)
                self.log.error(e)
                self.log.error(traceback.print_exc())
                return

    def leveling_loop(self) -> None:
        """Loop that runs the correct function based on the phase of the League Client, continuously starts games"""
        self.connection.connect_lcu(verbose=False)
        self.check_patch()
        while not self.account_leveled():
            match self.get_phase():
                case 'None':
                    self.create_lobby(GAME_LOBBY_ID)
                case 'Lobby':
                    self.start_matchmaking(GAME_LOBBY_ID)
                case 'Matchmaking':
                    self.queue()
                case 'ReadyCheck':
                    self.accept_match()
                case 'ChampSelect':
                    self.game_lobby()
                case 'InProgress':
                    game: Game = Game()
                    game.play_game()
                case 'Reconnect':
                    self.reconnect()
                case 'WaitingForStats':
                    self.wait_for_stats()
                case 'PreEndOfGame':
                    self.pre_end_of_game()
                case 'EndOfGame':
                    self.end_of_game()
                case _:
                    raise ClientError("Unknown phase. {}".format(self.phase))

    def get_phase(self) -> str:
        """Requests the League Client phase"""
        for i in range(15):
            r = self.connection.request('get', '/lol-gameflow/v1/gameflow-phase')
            if r.status_code == 200:
                self.prev_phase = self.phase
                self.phase = r.json()
                self.log.debug("New Phase: {}, Previous Phase: {}".format(self.phase, self.prev_phase))
                if self.prev_phase == self.phase and self.phase != "Matchmaking":
                    self.phase_errors += 1
                    if self.phase_errors == MAX_PHASE_ERRORS:
                        raise ClientError("Transition error. Phase will not change")
                    else:
                        self.log.debug("Phase same as previous. Phase: {}, Previous Phase: {}, Errno {}".format(self.phase, self.prev_phase, self.phase_errors))
                else:
                    self.phase_errors = 0
                sleep(1.5)
                return self.phase
            sleep(1)
        raise ClientError("Could not get phase")

    def create_lobby(self, lobby_id: int) -> None:
        """Creates a lobby for given lobby ID"""
        self.log.info("Creating lobby with lobby_id: {}".format(lobby_id))
        self.connection.request('post', '/lol-lobby/v2/lobby', data={'queueId': lobby_id})
        sleep(1.5)

    def start_matchmaking(self, lobby_id: int) -> None:
        """Starts matchmaking for a given lobby ID, will also wait out dodge timers"""
        self.log.info("Starting queue for lobby_id: {}".format(lobby_id))
        r = self.connection.request('get', '/lol-lobby/v2/lobby')
        if r.json()['gameConfig']['queueId'] != lobby_id:
            self.create_lobby(lobby_id)
            sleep(1)
        self.connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
        sleep(1.5)

        # Check for dodge timer
        r = self.connection.request('get', '/lol-matchmaking/v1/search')
        if r.status_code == 200 and len(r.json()['errors']) != 0:
            dodge_timer = int(r.json()['errors'][0]['penaltyTimeRemaining'])
            self.log.info("Dodge Timer. Time Remaining: {}".format(utils.seconds_to_min_sec(dodge_timer)))
            sleep(dodge_timer)

    def queue(self) -> None:
        """Waits until the League Client Phase changes to something other than 'Matchmaking'"""
        self.log.info("In queue. Waiting for match")
        start = datetime.now()
        while True:
            if self.get_phase() != 'Matchmaking':
                return
            elif datetime.now() - start > timedelta(minutes=15):
                raise ClientError("Queue Timeout")
            elif datetime.now() - start > timedelta(minutes=10):
                self.connection.request('delete', '/lol-lobby/v2/lobby/matchmaking/search')
            sleep(1)

    def accept_match(self) -> None:
        """Accepts the Ready Check"""
        self.log.info("Accepting match")
        self.connection.request('post', '/lol-matchmaking/v1/ready-check/accept')

    def game_lobby(self) -> None:
        """Handles the Champ Select Lobby"""
        self.log.info("Lobby opened, picking champ")
        r = self.connection.request('get', '/lol-champ-select/v1/session')
        if r.status_code != 200:
            return
        cs = r.json()

        r2 = self.connection.request('get', '/lol-lobby-team-builder/champ-select/v1/pickable-champion-ids')
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
                        self.log.debug("Lobby State: {}. Time Left in Lobby: {}s. Action: Hovering champ".format(lobby_state, lobby_time_left))
                        if champ_index < len(CHAMPS):
                            champion_id = CHAMPS[champ_index]
                            champ_index += 1
                        else:
                            champion_id = f2p[f2p_index]
                            f2p_index += 1
                        url = '/lol-champ-select/v1/session/actions/{}'.format(action['id'])
                        data = {'championId': champion_id}
                        self.connection.request('patch', url, data=data)
                    else:  # champ selected, lock in
                        self.log.debug("Lobby State: {}. Time Left in Lobby: {}s. Action: Locking in champ".format(lobby_state, lobby_time_left))
                        url = '/lol-champ-select/v1/session/actions/{}'.format(action['id'])
                        data = {'championId': action['championId']}
                        self.connection.request('post', url + '/complete', data=data)

                        # Ask for mid
                        if not requested:
                            sleep(1)
                            try:
                                self.chat(random.choice(ASK_4_MID_DIALOG))
                            except IndexError:
                                pass
                            requested = True
                else:
                    self.log.debug("Lobby State: {}. Time Left in Lobby: {}s. Action: Waiting".format(lobby_state, lobby_time_left))
                r = self.connection.request('get', '/lol-champ-select/v1/session')
                if r.status_code != 200:
                    self.log.info('Lobby closed')
                    return
                cs = r.json()
                sleep(3)

    def reconnect(self) -> None:
        """Attempts to reconnect to an ongoing League of Legends match"""
        self.log.info("Reconnecting to game")
        for i in range(3):
            r = self.connection.request('post', '/lol-gameflow/v1/reconnect')
            if r.status_code == 204:
                return
            sleep(2)
        self.log.warning('Could not reconnect to game')

    def wait_for_stats(self) -> None:
        """Waits for the League Client Phase to change to something other than 'WaitingForStats'"""
        self.log.info("Waiting for stats")
        for i in range(60):
            sleep(2)
            if self.get_phase() != 'WaitingForStats':
                return
        raise ClientError("Waiting for stats timeout")

    def pre_end_of_game(self) -> None:
        """Handles league of legends client reopening after a game, honoring teammates, and clearing level-up/mission rewards"""
        self.log.info("Honoring teammates and accepting rewards")
        sleep(3)
        try:
            utils.click(POPUP_SEND_EMAIL_X_RATIO, LEAGUE_CLIENT_WINNAME, 2)
            self.honor_player()
            utils.click(POPUP_SEND_EMAIL_X_RATIO, LEAGUE_CLIENT_WINNAME, 2)
            for i in range(3):
                utils.click(POST_GAME_SELECT_CHAMP_RATIO, LEAGUE_CLIENT_WINNAME, 1)
                utils.click(POST_GAME_OK_RATIO, LEAGUE_CLIENT_WINNAME, 1)
            utils.click(POPUP_SEND_EMAIL_X_RATIO, LEAGUE_CLIENT_WINNAME, 1)
        except (utils.WindowNotFound, pyautogui.FailSafeException):
            sleep(3)

    def end_of_game(self) -> None:
        """Transitions League Client to 'Lobby' phase."""
        self.log.info("Post game. Starting a new loop")
        posted = False
        for i in range(15):
            if self.get_phase() != 'EndOfGame':
                return
            if not posted:
                self.connection.request('post', '/lol-lobby/v2/play-again')
            else:
                self.create_lobby(GAME_LOBBY_ID)
            posted = not posted
            sleep(1)
        raise ClientError("Could not exit play-again screen")

    def account_leveled(self) -> bool:
        """Checks if account has reached the constants.MAX_LEVEL (default 30)"""
        r = self.connection.request('get', '/lol-chat/v1/me')
        if r.status_code == 200:
            self.account_level = int(r.json()['lol']['level'])
            if self.account_level < ACCOUNT_MAX_LEVEL:
                self.log.debug("Account Level: {}.".format(self.account_level))
                return False
            else:
                self.log.info("SUCCESS: Account Leveled")
                return True

    def check_patch(self) -> None:
        """Checks if the League Client is patching and waits till it is finished"""
        self.log.info("Checking for Client Updates")
        r = self.connection.request('get', '/patcher/v1/products/league_of_legends/state')
        if r.status_code != 200:
            return
        logged = False
        while not r.json()['isUpToDate']:
            if not logged:
                self.log.info("Client is patching...")
                logged = True
            sleep(3)
            r = self.connection.request('get', '/patcher/v1/products/league_of_legends/state')
            self.log.debug('Status Code: {}, Percent Patched: {}%'.format(r.status_code, r.json()['percentPatched']))
            self.log.debug(r.json())
        self.log.info("Client is up to date")

    def honor_player(self) -> None:
        """Honors a player in the post game lobby"""
        for i in range(3):
            r = self.connection.request('get', '/lol-honor-v2/v1/ballot')
            if r.status_code == 200:
                players = r.json()['eligiblePlayers']
                index = random.randint(0, len(players)-1)
                self.connection.request('post', '/lol-honor-v2/v1/honor-player', data={"summonerId": players[index]['summonerId']})
                self.log.debug("Honor Success: Player {}. Champ: {}. Summoner: {}. ID: {}".format(index+1, players[index]['championName'], players[index]['summonerName'], players[index]['summonerId']))
                sleep(2)
                return
            sleep(2)
        self.log.warning('Honor Failure. Player -1, Champ: NULL. Summoner: NULL. ID: -1')
        self.connection.request('post', '/lol-honor-v2/v1/honor-player', data={"summonerId": 0})  # will clear honor screen

    def chat(self, msg: str) -> None:
        """Sends a message to the chat window"""
        chat_id = ''
        r = self.connection.request('get', '/lol-chat/v1/conversations')
        if r.status_code != 200:
            self.log.warning("{} chat attempt failed. Could not reach endpoint".format(inspect.stack()[1][3]))
            return
        for convo in r.json():
            if convo['gameName'] != '' and convo['gameTag'] != '':
                continue
            chat_id = convo['id']
        if chat_id == '':
            self.log.warning('{} chat attempt failed. Could not send message. Chat ID is Null'.format(inspect.stack()[1][3]))
            return
        data = {"body": msg}
        r = self.connection.request('post', '/lol-chat/v1/conversations/{}/messages'.format(chat_id), data=data)
        if r.status_code != 200:
            self.log.warning('Could not send message. HTTP STATUS: {} - {}, Caller: {}'.format(r.status_code, r.json(), inspect.stack()[1][3]))
        else:
            self.log.debug("Message success. Msg: {}. Caller: {}".format(msg, inspect.stack()[1][3]))
