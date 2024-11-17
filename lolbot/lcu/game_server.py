"""
Handles all HTTP requests to the local game server,
providing functions for interacting with various game endpoints.
"""

import json

import requests

GAME_SERVER_URL = 'https://127.0.0.1:2999/liveclientdata/allgamedata'


class GameServerError(Exception):
    pass


class GameServer:
    """Retrieves live game info from the local game server"""

    def __init__(self):
        self.data = None

    def update_data(self) -> None:
        try:
            response = requests.get(GAME_SERVER_URL, timeout=10, verify=False)
            response.raise_for_status()
            self.data = response.text
        except Exception as e:
            raise GameServerError(f"Failed to get game data: {e}")

    def is_running(self) -> bool:
        try:
            self.update_data()
            return True
        except GameServerError:
            return False

    def get_game_time(self) -> int:
        try:
            self.update_data()
            data = json.loads(self.data)
            return int(data['gameData']['gameTime'])
        except (GameServerError, json.JSONDecodeError, KeyError) as e:
            raise GameServerError(f"Failed to get game time: {e}")

    def get_formatted_time(self) -> str:
        try:
            self.update_data()
            seconds = self.get_game_time()
            if len(str(int(seconds % 60))) == 1:
                return str(int(seconds / 60)) + ":0" + str(int(seconds % 60))
            else:
                return str(int(seconds / 60)) + ":" + str(int(seconds % 60))
        except (GameServerError, ValueError):
            return "XX:XX"

    def get_champ(self) -> str:
        try:
            self.update_data()
            data = json.loads(self.data)
            for player in data['allPlayers']:
                if player['summonerName'] == data['activePlayer']['summonerName']:
                    return player['championName']
            return ""
        except (GameServerError, json.JSONDecodeError, KeyError) as e:
            raise GameServerError(f"Failed to get champion information: {e}")

    def summoner_is_dead(self) -> bool:
        try:
            self.update_data()
            data = json.loads(self.data)
            dead = False
            for player in data['allPlayers']:
                if player['summonerName'] == data['activePlayer']['summonerName']:
                    dead = bool(player['isDead'])
            return dead
        except (GameServerError, json.JSONDecodeError, KeyError) as e:
            raise GameServerError(f"Failed to get champion alive status: {e}")

    def get_summoner_health(self) -> float:
        try:
            self.update_data()
            data = json.loads(self.data)
            current_health = float(data['activePlayer']['championStats']['currentHealth'])
            max_health = float(data['activePlayer']['championStats']['maxHealth'])
            return current_health / max_health if max_health > 0 else 0
        except (GameServerError, json.JSONDecodeError, KeyError) as e:
            raise GameServerError(f"Failed to get champion health status: {e}")
