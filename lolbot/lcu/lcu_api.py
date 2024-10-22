"""
Handles all HTTP request to the local LoL Client,
providing functions for interacting with various LoL endpoints
"""

import requests

client = requests.Session()
client.verify = False
client.headers.update({'Accept': 'application/json'})
client.timeout = 2
client.trust_env = False


class LCUError(Exception):
    """Exception for LCU API errors"""
    pass


def get_phase(endpoint: str) -> str:
    """Retrieves the League Client phase"""
    url = f"{endpoint}/lol-gameflow/v1/gameflow-phase"
    try:
        response = client.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise LCUError(f"Failed to get game phase: {str(e)}")


def create_lobby(endpoint: str, lobby_id: int) -> None:
    """Creates a lobby for given lobby ID"""
    url = f"{endpoint}/lol-lobby/v2/lobby"
    try:
        response = client.post(url, data={'queueID': lobby_id})
        response.raise_for_status()
    except requests.RequestException as e:
        raise LCUError(f"Failed to create lobby with id {lobby_id}: {str(e)}")


def start_matchmaking(endpoint: str) -> None:
    """Starts matchmaking for current lobby"""
    url = f"{endpoint}/lol-lobby/v2/lobby/matchmaking/search"
    try:
        response = client.post(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise LCUError(f"Failed to start matchmaking: {str(e)}")


def exit_matchmaking(endpoint: str) -> None:
    """Cancels matchmaking search"""
    url = f"{endpoint}/lol-lobby/v2/lobby/matchmaking/search"
    try:
        response = client.delete(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise LCUError(f"Error cancelling matchmaking: {str(e)}")


def accept_match(endpoint: str) -> None:
    """Accepts the Ready Check"""
    url = f"{endpoint}/lol-matchmaking/v1/ready-check/accept"
    try:
        response = client.post(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise LCUError(f"Failed to accept match: {str(e)}")


def in_champ_select(endpoint: str) -> bool:
    """Determines if currently in champ select lobby"""
    url = f"{endpoint}/lol-champ-select/v1/session"
    try:
        response = client.get(url)
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException as e:
        raise LCUError(f"Error retrieving session information: {str(e)}")


def get_champ_select(endpoint: str) -> {}:
    """Gets the champ select lobby information"""
    url = f"{endpoint}/lol-lobby-team-builder/champ-select/v1/pickable-champion-ids"
    try:
        response = client.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise LCUError(f"Could not get champ select data: {str(e)}")


def game_reconnect(endpoint: str):
    """Reconnects to active game"""
    url = f"{endpoint}/lol-gameflow/v1/reconnect"
    try:
        response = client.post(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise LCUError(f"Could not reconnect to game: {str(e)}")


def play_again(endpoint: str):
    """Moves the League Client from endgame screen back to lobby"""
    url = f"{endpoint}/lol-lobby/v2/play-again"
    try:
        response = client.post(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise LCUError(f"Could not exit play-again screen: {str(e)}")


def get_account_level(endpoint: str) -> int:
    """Gets level of currently logged in account"""
    url = f"{endpoint}/lol-summoner/v1/current-summoner"
    try:
        response = client.get(url)
        response.raise_for_status()
        return int(response.json()['summoner_level'])
    except requests.RequestException as e:
        raise LCUError(f"Error retrieving account level: {str(e)}")


def is_client_patching(endpoint: str) -> bool:
    """Checks if the client is currently patching"""
    url = f"{endpoint}/patcher/v1/products/league_of_legends/state"
    try:
        response = client.get(url)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        return False


def honor_player(endpoint: str, summoner_id: int) -> None:
    """Honors player in post game screen"""
    url = f"{endpoint}/lol-honor-v2/v1/honor-player"
    try:
        response = client.post(url, data={"summonerID": summoner_id})
        response.raise_for_status()
    except requests.RequestException as e:
        raise LCUError(f"Failed to honor player: {str(e)}")


def send_chat_message(endpoint: str, msg: str) -> None:
    """Sends a message to the chat window"""
    open_chats_url = f"{endpoint}/lol-chat/v1/conversations"
    send_chat_message_url = f"{endpoint}/lol-chat/v1/conversations/{msg}/messages"
    try:
        response = client.get(open_chats_url)
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
        response = client.post(send_chat_message_url, message)
        response.raise_for_status()
    except requests.RequestException as e:
        raise LCUError(f"Failed to send message: {str(e)}")
































