"""
Handles all HTTP requests to the local game server,
providing functions for interacting with various game endpoints.
"""

import json

import requests

GAME_SERVER_URL = 'https://127.0.0.1:2999/liveclientdata/allgamedata'
GAME_PROCESS_NAME = "League of Legends.exe"


class GameAPIError(Exception):
    pass


def is_connected() -> bool:
    """Check if getting response from game server"""
    try:
        response = requests.get(GAME_SERVER_URL, timeout=10, verify=False)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        return False


def get_game_data() -> str:
    """Retrieves game data from the local game server"""
    try:
        response = requests.get(GAME_SERVER_URL, timeout=10, verify=False)
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise GameAPIError(f"Failed to get game data: {str(e)}")


def get_game_time() -> int:
    """Gets current time in game"""
    try:
        json_string = get_game_data()
        data = json.loads(json_string)
        return int(data['gameData']['gameTime'])
    except json.JSONDecodeError as e:
        raise GameAPIError(f"Invalid JSON data: {e}")
    except KeyError as e:
        raise GameAPIError(f"Missing key in data: {e}")
    except GameAPIError as e:
        raise e


def get_formatted_time() -> str:
    """Converts League of Legends game time to minute:seconds format"""
    try:
        seconds = int(get_game_time())
        if len(str(int(seconds % 60))) == 1:
            return str(int(seconds / 60)) + ":0" + str(int(seconds % 60))
        else:
            return str(int(seconds / 60)) + ":" + str(int(seconds % 60))
    except GameAPIError:
        return "XX:XX"
    except ValueError:
        return "XX:XX"


def get_champ() -> str:
    """Gets current champion being  played in game"""
    try:
        json_string = get_game_data()
        data = json.loads(json_string)
        for player in data['allPlayers']:
            if player['summonerName'] == data['activePlayer']['summonerName']:
                return player['championName']
        return ""
    except json.JSONDecodeError as e:
        raise GameAPIError(f"Invalid JSON data: {e}")
    except KeyError as e:
        raise GameAPIError(f"Missing key in data: {e}")
    except GameAPIError as e:
        raise e


def is_dead() -> bool:
    """Returns whether player is currently dead"""
    try:
        json_string = get_game_data()
        data = json.loads(json_string)

        dead = False
        for player in data['allPlayers']:
            if player['summonerName'] == data['activePlayer']['summonerName']:
                dead = bool(player['isDead'])
        return dead
    except json.JSONDecodeError as e:
        raise GameAPIError(f"Invalid JSON data: {e}")
    except KeyError as e:
        raise GameAPIError(f"Missing key in data: {e}")
    except GameAPIError as e:
        raise e
