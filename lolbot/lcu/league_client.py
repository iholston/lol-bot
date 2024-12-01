"""
Handles all HTTP request to the local LoL Client,
providing functions for interacting with various LoL endpoints.
"""
import threading

import requests
import urllib3

from lolbot.system import cmd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LCUError(Exception):
    """Exception for LCU API errors"""
    pass


class LeagueClient:

    def __init__(self):
        self.client = requests.Session()
        self.client.verify = False
        self.client.headers.update({'Accept': 'application/json'})
        self.client.timeout = 2
        self.client.trust_env = False
        self.timer = None
        self.endpoint = cmd.get_auth_string()

    def update_auth(self):
        self.endpoint = cmd.get_auth_string()

    def update_auth_timer(self, timer: int = 5):
        self.endpoint = cmd.get_auth_string()
        self.timer = threading.Timer(timer, self.update_auth_timer)
        self.timer.start()

    def stop_timer(self):
        self.timer.cancel()
        self.timer = None

    def make_get_request(self, url):
        url = f"{self.endpoint}{url}"
        try:
            response = self.client.get(url)
            return response
        except Exception as e:
            raise e

    def make_post_request(self, url, body):
        url = f"{self.endpoint}{url}"
        try:
            response = self.client.post(url, json=body)
            return response
        except Exception as e:
            raise e

    def make_patch_request(self, url, body):
        url = f"{self.endpoint}{url}"
        try:
            response = self.client.patch(url, json=body)
            return response
        except Exception as e:
            raise e

    def make_delete_request(self, url, body):
        url = f"{self.endpoint}{url}"
        try:
            response = self.client.delete(url, json=body)
            return response
        except Exception as e:
            raise e

    def make_put_request(self, url, body):
        url = f"{self.endpoint}{url}"
        try:
            response = self.client.put(url, json=body)
            return response
        except Exception as e:
            raise e

    def get_summoner_name(self) -> str:
        """Gets display name of logged in account"""
        url = f"{self.endpoint}/lol-summoner/v1/current-summoner"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            if response.json()['displayName']:
                return response.json()['displayName']
            else:
                return response.json()['gameName']
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving display name: {e}")

    def get_summoner_level(self) -> int:
        """Gets level logged in account"""
        url = f"{self.endpoint}/lol-summoner/v1/current-summoner"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return int(response.json()['summonerLevel'])
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving summoner level: {e}")

    def get_patch(self) -> str:
        """Gets current patch"""
        url = f"{self.endpoint}/lol-patch/v1/game-version"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text[1:6]
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving patch: {e}")

    def get_lobby_id(self) -> int:
        """Gets name of current lobby"""
        url = f"{self.endpoint}/lol-lobby/v2/lobby"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return int(response.json()['gameConfig']['queueId'])
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving lobby ID: {e}")

    def restart_ux(self) -> None:
        """Restarts league client ux"""
        url = f"{self.endpoint}/riotclient/kill-and-restart-ux"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Error restarting UX: {e}")

    def access_token_exists(self) -> bool:
        """Checks if access token exists"""
        url = f"{self.endpoint}/rso-auth/v1/authorization"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            return False

    def get_dodge_timer(self) -> int:
        """Gets dodge penalty timer"""
        url = f"{self.endpoint}/lol-matchmaking/v1/search"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            if len(response.json()['errors']) != 0:
                return int(response.json()['errors'][0]['penaltyTimeRemaining'])
            else:
                return 0
        except requests.RequestException as e:
            raise LCUError(f"Error getting dodge timer: {e}")

    def get_estimated_queue_time(self) -> int:
        """Retrieves estimated queue time"""
        url = f"{self.endpoint}/lol-matchmaking/v1/search"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return int(response.json()['estimatedQueueTime'])
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving estimated queue time: {e}")

    def login(self, username: str, password: str) -> None:
        """Logs into the Riot Client"""
        url = f"{self.endpoint}/rso-auth/v2/authorizations"
        body = {"clientId": "riot-client", 'trustLevels': ['always_trusted']}
        try:
            response = self.client.post(url, json=body)
            response.raise_for_status()
            print(response.json())
        except requests.RequestException as e:
            print(f"1{e}")
            raise LCUError(f"Error in login authorization: {e}")

        url = f"{self.endpoint}/rso-auth/v1/session/credentials"
        body = {"username": username, "password": password, "persistLogin": False}
        try:
            response = self.client.put(url, json=body)
            response.raise_for_status()
            print(response.json())
        except requests.RequestException as e:
            print(e)
            raise LCUError(f"Invalid Username or Password: {e}")

    def launch_league_from_rc(self) -> None:
        """Ensures that the account does not stay signed in after client exits"""
        url = f"{self.endpoint}/product-launcher/v1/products/league_of_legends/patchlines/live"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to launch league from Riot Client: {e}")

    def logout_on_close(self) -> None:
        """Ensures that the account does not stay signed in after client exits"""
        url = f"{self.endpoint}/lol-login/v1/delete-rso-on-close"
        try:
            response = self.client.post(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LCUError(f"Failed to prevent auto-signin next launch: {e}")

    def get_phase(self) -> str:
        """Retrieves the League Client phase"""
        url = f"{self.endpoint}/lol-gameflow/v1/gameflow-phase"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LCUError(f"Failed to get game phase: {e}")

    def create_lobby(self, lobby_id: int) -> None:
        """Creates a lobby for given lobby ID"""
        url = f"{self.endpoint}/lol-lobby/v2/lobby"
        try:
            response = self.client.post(url, json={'queueId': lobby_id})
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to create lobby with id {lobby_id}: {e}")

    def start_matchmaking(self) -> None:
        """Starts matchmaking for current lobby"""
        url = f"{self.endpoint}/lol-lobby/v2/lobby/matchmaking/search"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to start matchmaking: {e}")

    def get_matchmaking_time(self) -> str:
        """Gets current time in queue"""
        url = f"{self.endpoint}/lol-matchmaking/v1/search"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return str(int(response.json()['timeInQueue']))
        except requests.RequestException as e:
            raise LCUError(f"Could not get time in queue: {e}")

    def quit_matchmaking(self) -> None:
        """Cancels matchmaking search"""
        url = f"{self.endpoint}/lol-lobby/v2/lobby/matchmaking/search"
        try:
            response = self.client.delete(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Error cancelling matchmaking: {e}")

    def accept_match(self) -> None:
        """Accepts the Ready Check"""
        url = f"{self.endpoint}/lol-matchmaking/v1/ready-check/accept"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to accept match: {e}")

    def get_champ_select_data(self) -> dict:
        """Gets champ select lobby data"""
        url = f"{self.endpoint}/lol-champ-select/v1/session"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving champ select information: {e}")

    def get_available_champion_ids(self) -> list:
        """Hovers a champion in champ select"""
        url = f"{self.endpoint}/lol-lobby-team-builder/champ-select/v1/pickable-champion-ids"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LCUError(f"Error getting available champs {e}")

    def hover_champion(self, action_id: str, champion_id) -> None:
        """Hovers a champion in champ select"""
        url = f"{self.endpoint}/lol-champ-select/v1/session/actions/{action_id}"
        data = {'championId': champion_id}
        try:
            response = self.client.patch(url, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Error hovering champion in champ select {e}")

    def lock_in_champion(self, action_id: str, champion_id) -> None:
        """Locks in a champion in champ select"""
        url = f"{self.endpoint}/lol-champ-select/v1/session/actions/{action_id}/complete"
        data = {'championId': champion_id}
        try:
            response = self.client.post(url, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Error locking in champion {e}")

    def get_cs_time_remaining(self) -> str:
        """Returns time remaining in Champ Select"""
        url = f"{self.endpoint}/lol-champ-select/v1/session"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()['timer']['adjustedTimeLeftInPhase']
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving champ select information: {e}")

    def game_reconnect(self):
        """Reconnects to active game"""
        url = f"{self.endpoint}/lol-gameflow/v1/reconnect"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Could not reconnect to game: {e}")

    def play_again(self):
        """Moves the League Client from endgame screen back to lobby"""
        url = f"{self.endpoint}/lol-lobby/v2/play-again"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Could not exit play-again screen: {e}")

    def is_client_patching(self) -> bool:
        """Checks if the client is currently patching"""
        url = f"{self.endpoint}/patcher/v1/products/league_of_legends/state"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return not response.json()['isUpToDate']
        except requests.RequestException as e:
            return False

    def get_players_to_honor(self) -> list:
        """Returns list of player summonerIds that can then be honored"""
        url = f"{self.endpoint}/lol-honor-v2/v1/ballot"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()['eligibleAllies']
        except requests.RequestException as e:
            raise LCUError(f"Failed to retrieve players to honor player: {e}")

    def honor_player(self, summoner_id: int) -> None:
        """Honors player in post game screen"""
        url = f"{self.endpoint}/lol-honor-v2/v1/honor-player"
        try:
            response = self.client.post(url, json={"summonerID": summoner_id})
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to honor player: {e}")

    def send_chat_message(self, msg: str) -> None:
        """Sends a message to the chat window"""
        open_chats_url = f"{self.endpoint}/lol-chat/v1/conversations"
        send_chat_message_url = f"{self.endpoint}/lol-chat/v1/conversations/{msg}/messages"
        try:
            response = self.client.get(open_chats_url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to send message, could not retrieve chats: {e}")

        chat_id = None
        for conversation in response.json():
            if conversation['gameName'] != '' and conversation['gameTag'] != '':
                continue
            chat_id = conversation['id']
        if chat_id is None:
            raise LCUError(f"Failed to send message: Chat ID is NULL")

        message = {"body": msg}
        try:
            response = self.client.post(send_chat_message_url, json=message)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to send message: {e}")
