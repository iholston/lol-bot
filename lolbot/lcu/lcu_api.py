"""
Handles all HTTP request to the local LoL Client,
providing functions for interacting with various LoL endpoints
"""
import threading

import requests

import lolbot.lcu.cmd as cmd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LCUError(Exception):
    """Exception for LCU API errors"""
    pass


class LCUApi:

    def __init__(self):
        self.client = requests.Session()
        self.client.verify = False
        self.client.headers.update({'Accept': 'application/json'})
        self.client.timeout = 2
        self.client.trust_env = False
        self.endpoint = cmd.get_commandline().auth_url

    def update_auth(self):
        self.endpoint = cmd.get_commandline().auth_url

    def update_auth_timer(self, timer: int = 5):
        self.endpoint = cmd.get_commandline().auth_url
        threading.Timer(timer, self.update_auth_timer).start()

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

    def get_display_name(self) -> str:
        """Gets display name of logged in account"""
        url = f"{self.endpoint}/lol-summoner/v1/current-summoner"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()['displayName']
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving display name: {str(e)}")

    def get_summoner_level(self) -> int:
        """Gets level logged in account"""
        url = f"{self.endpoint}/lol-summoner/v1/current-summoner"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return int(response.json()['summonerLevel'])
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving display name: {str(e)}")

    def get_patch(self) -> str:
        """Gets current patch"""
        url = f"{self.endpoint}/lol-patch/v1/game-version"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text[:5]
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving patch: {str(e)}")

    def get_lobby_id(self) -> int:
        """Gets name of current lobby"""
        url = f"{self.endpoint}/lol-lobby/v2/lobby"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return int(response.json()['gameConfig']['queueId'])
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving lobby ID: {str(e)}")

    def restart_ux(self) -> None:
        """Restarts league client ux"""
        url = f"{self.endpoint}/riotclient/kill-and-restart-ux"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Error restarting UX: {str(e)}")

    def access_token_exists(self) -> bool:
        """Checks if access token exists"""
        url = f"{self.endpoint}/rso-auth/v1/authorization/access-token"
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
            raise LCUError(f"Error getting dodge timer: {str(e)}")

    def get_estimated_queue_time(self) -> int:
        """Retrieves estimated queue time"""
        url = f"{self.endpoint}/lol-matchmaking/v1/search"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return int(response.json()['estimatedQueueTime'])
        except requests.RequestException as e:
            raise LCUError(f"Error getting dodge timer: {str(e)}")

    def login(self, username: str, password: str) -> None:
        # body = {"clientId": "riot-client", 'trustLevels': ['always_trusted']}
        # r = self.connection.request("post", "/rso-auth/v2/authorizations", data=body)
        # if r.status_code != 200:
        #     raise LauncherError("Failed Authorization Request. Response: {}".format(r.status_code))
        # body = {"username": self.username, "password": self.password, "persistLogin": False}
        # r = self.connection.request("put", '/rso-auth/v1/session/credentials', data=body)
        return

    def get_phase(self) -> str:
        """Retrieves the League Client phase"""
        url = f"{self.endpoint}/lol-gameflow/v1/gameflow-phase"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LCUError(f"Failed to get game phase: {str(e)}")

    def create_lobby(self, lobby_id: int) -> None:
        """Creates a lobby for given lobby ID"""
        url = f"{self.endpoint}/lol-lobby/v2/lobby"
        try:
            response = self.client.post(url, json={'queueId': lobby_id})
            print(response.json())
            response.raise_for_status()
        except requests.RequestException as e:
            print(str(e))
            raise LCUError(f"Failed to create lobby with id {lobby_id}: {str(e)}")

    def start_matchmaking(self) -> None:
        """Starts matchmaking for current lobby"""
        url = f"{self.endpoint}/lol-lobby/v2/lobby/matchmaking/search"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to start matchmaking: {str(e)}")

    def quit_matchmaking(self) -> None:
        """Cancels matchmaking search"""
        url = f"{self.endpoint}/lol-lobby/v2/lobby/matchmaking/search"
        try:
            response = self.client.delete(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Error cancelling matchmaking: {str(e)}")

    def accept_match(self) -> None:
        """Accepts the Ready Check"""
        url = f"{self.endpoint}/lol-matchmaking/v1/ready-check/accept"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to accept match: {str(e)}")

    def in_champ_select(self) -> bool:
        """Determines if currently in champ select lobby"""
        url = f"{self.endpoint}/lol-champ-select/v1/session"
        try:
            response = self.client.get(url)
            if response.status_code == 200:
                return True
            return False
        except requests.RequestException as e:
            raise LCUError(f"Error retrieving session information: {str(e)}")

    def get_available_champ_ids(self) -> {}:
        """Gets the champ select lobby information"""
        url = f"{self.endpoint}/lol-lobby-team-builder/champ-select/v1/pickable-champion-ids"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LCUError(f"Could not get champ select data: {str(e)}")

    def game_reconnect(self):
        """Reconnects to active game"""
        url = f"{self.endpoint}/lol-gameflow/v1/reconnect"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Could not reconnect to game: {str(e)}")

    def play_again(self):
        """Moves the League Client from endgame screen back to lobby"""
        url = f"{self.endpoint}/lol-lobby/v2/play-again"
        try:
            response = self.client.post(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Could not exit play-again screen: {str(e)}")

    def is_client_patching(self) -> bool:
        """Checks if the client is currently patching"""
        url = f"{self.endpoint}/patcher/v1/products/league_of_legends/state"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            if not response.json()['isUpToDate']:
                return True
            return False
        except requests.RequestException as e:
            return False

    def honor_player(self, summoner_id: int) -> None:
        """Honors player in post game screen"""
        url = f"{self.endpoint}/lol-honor-v2/v1/honor-player"
        try:
            response = self.client.post(url, data={"summonerID": summoner_id})
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to honor player: {str(e)}")

    def send_chat_message(self, msg: str) -> None:
        """Sends a message to the chat window"""
        open_chats_url = f"{self.endpoint}/lol-chat/v1/conversations"
        send_chat_message_url = f"{self.endpoint}/lol-chat/v1/conversations/{msg}/messages"
        try:
            response = self.client.get(open_chats_url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise LCUError(f"Failed to send message: {str(e)}")

        chat_id = None
        for conversation in response.json():
            if conversation['gameName'] != '' and conversation['gameTag'] != '':
                continue
            chat_id = conversation['id']
        if chat_id is None:
            raise LCUError(f"Failed to send message: Chat ID is NULL")

        message = {"body": msg}
        try:
            response = self.client.post(send_chat_message_url, data=message)
            response.raise_for_status()
        except requests.RequestException as e:
            #raise LCUError(f"Failed to send message: {str(e)}")
            pass
