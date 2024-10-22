"""
Handles all HTTP requests to the local game server,
providing functions for interactive with various game endpoints
"""

import json
from typing import NamedTuple

import requests


GAME_SERVER_URL = 'https://127.0.0.1:2999/liveclientdata/allgamedata'


class GameDataError(Exception):
    pass


class GameData(NamedTuple):
    summoner_name: str
    is_dead: bool
    game_time: int


def get_game_data() -> GameData:
    """Returns available character information"""
    try:
        json_response = fetch_game_data()
        return parse_game_data(json_response)
    except GameDataError as e:
        raise e


def fetch_game_data() -> str:
    """Retrieves game data from the local game server"""
    try:
        response = requests.get(GAME_SERVER_URL, timeout=10, verify=False)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        raise GameDataError("The request timed out")
    except requests.exceptions.ConnectionError:
        raise GameDataError("Failed to connect to the server")
    except requests.exceptions.HTTPError as e:
        raise GameDataError(f"HTTP error occurred: {e}")


def parse_game_data(json_string: str) -> GameData:
    """Parses the game data json response for relevant information"""
    try:
        data = json.loads(json_string)

        name = data['activePlayer']['summonerName']
        is_dead = False
        time = int(data['gameData']['gameTime'])

        for player in data['allPlayers']:
            if player['summonerName'] == name:
                is_dead = bool(player['isDead'])

        return GameData(
            summoner_name=name,
            is_dead=is_dead,
            game_time=time,
        )
    except json.JSONDecodeError as e:
        raise GameDataError(f"Invalid JSON data: {e}")
    except KeyError as e:
        raise GameDataError(f"Missing key in data: {e}")
