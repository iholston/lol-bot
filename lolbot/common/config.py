"""
Handles creating/writing configurations to json file
"""

import os
import json
from typing import Any


class Constants:
    """Constant settings"""
    # Constant paths
    RIOT_LOCKFILE = os.path.join(os.getenv('LOCALAPPDATA'), 'Riot Games/Riot Client/Config/lockfile')
    CONFIG_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'LoLBot')
    BAK_DIR = os.path.join(CONFIG_DIR, 'bak')
    LOG_DIR = os.path.join(CONFIG_DIR, 'logs')
    CONFIG_PATH = os.path.join(CONFIG_DIR, 'configs.json')
    ACCOUNT_PATH = os.path.join(CONFIG_DIR, 'accounts.json')

    # Pyinstaller dependant paths
    GAME_CFG = 'lolbot/resources/game.cfg'
    ICON_PATH = 'lolbot/resources/images/a.ico'

    # Other
    VERSION = '2.2.2'

    @staticmethod
    def create_dirs():
        if not os.path.exists(Constants.CONFIG_DIR):
            os.makedirs(Constants.CONFIG_DIR)
        if not os.path.exists(Constants.LOG_DIR):
            os.makedirs(Constants.LOG_DIR)
        if not os.path.exists(Constants.BAK_DIR):
            os.makedirs(Constants.BAK_DIR)
        if not os.path.exists(Constants.CONFIG_PATH):
            open(Constants.CONFIG_PATH, 'w+')
        if not os.path.exists(Constants.ACCOUNT_PATH):
            open(Constants.ACCOUNT_PATH, 'w+')


class DefaultSettings:
    """Default settings for bot"""
    LEAGUE_DIR = 'C:/Riot Games/League of Legends'
    LOBBY = 840
    MAX_LEVEL = 30
    PATCH = '13.21.1'
    CHAMPS = [21, 18, 22, 67]
    DIALOG = ["mid ples", "plannin on goin mid team", "mid por favor", "bienvenidos, mid", "howdy, mid", "goin mid", "mid"]
    ALLY_MID_TURRET = [0.8760, 0.8846]
    ATTACK_MID_TURRET = [0.8981, 0.8674]
    ATTACK_NEXUS = [0.9628, 0.7852]


class ConfigRW:
    """Reads/Writes configurations required by bot"""

    def __init__(self):
        self.file = open(Constants.CONFIG_PATH, 'r+')
        self.settings = {}
        self.load_or_default()
        self._json_update()

    def _json_update(self):
        """Persists settings"""
        self.file.seek(0)
        json.dump(self.settings, self.file, indent=4)
        self.file.truncate()

    def load_or_default(self):
        """Attempts to load settings, if it fails, sets to default"""
        try:
            self.settings = json.load(self.file)
        except json.decoder.JSONDecodeError:
            self.set_defaults()

    def set_defaults(self):
        """Set and persist the default settings"""
        self.set_league_dir(DefaultSettings.LEAGUE_DIR)
        self.settings['lobby'] = DefaultSettings.LOBBY
        self.settings['max_level'] = DefaultSettings.MAX_LEVEL
        self.settings['patch'] = DefaultSettings.PATCH
        self.settings['champs'] = DefaultSettings.CHAMPS
        self.settings['dialog'] = DefaultSettings.DIALOG
        self.settings['ally_mid_turret'] = DefaultSettings.ALLY_MID_TURRET
        self.settings['attack_mid_turret'] = DefaultSettings.ATTACK_MID_TURRET
        self.settings['attack_nexus'] = DefaultSettings.ATTACK_NEXUS
        self._json_update()

    def set_league_dir(self, league_dir: str):
        """Sets all league paths since they depend on one directory"""
        self.settings['league_dir'] = league_dir
        self.settings['league_path'] = os.path.join(league_dir, 'LeagueClient')
        self.settings['league_config'] = os.path.join(league_dir, 'Config/game.cfg')
        self.settings['league_lockfile'] = os.path.join(league_dir, 'lockfile')
        self._json_update()

    def set_data(self, key: str, value: Any):
        """Persists data to JSON"""
        self.settings[key] = value
        self._json_update()

    def get_data(self, key: str):
        """Retrieves data from JSON. If no value found, adds it from default values"""
        if key in self.settings.keys():
            return self.settings[key]
        else:
            value = getattr(DefaultSettings, key.upper(), None)
            self.settings[key] = getattr(DefaultSettings, key.upper(), None)
            self._json_update()
            return value

