"""
Handles creating/writing configurations to json file
"""

import os
import json

import requests


class DefaultSettings:
    """Default settings for bot"""

    # Paths
    CONFIG_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'lolbot')
    LOG_DIR = os.path.join(CONFIG_DIR, 'logs')
    CONFIG_PATH = os.path.join(CONFIG_DIR, 'configs.json')
    ACCOUNT_PATH = os.path.join(CONFIG_DIR, 'accounts.json')
    RIOT_LOCKFILE = os.path.join(os.getenv('LOCALAPPDATA'), '/Riot Games/Riot Client/Config/lockfile')
    GAME_CFG = os.getcwd() + '/lolbot/resources/game.cfg'
    ICON_PATH = os.getcwd() + '/lolbot/resources/images/a.ico'

    # Bot
    LEAGUE_DIR = 'C:/Riot Games/League of Legends'
    LOBBY = 840
    MAX_LEVEL = 30
    PATCH = '13.21.1'
    CHAMPS = []
    DIALOG = ["mid ples", "plannin on goin mid team", "mid por favor", "bienvenidos, mid", "howdy, mid", "goin mid", "mid"]

    # Other
    VERSION = '2.2.1'


class ConfigRW:
    """Reads/Writes configurations required by bot"""

    def __init__(self):
        if not os.path.exists(DefaultSettings.CONFIG_DIR):
            os.makedirs(DefaultSettings.CONFIG_DIR)
        if not os.path.exists(DefaultSettings.CONFIG_PATH):
            open(DefaultSettings.CONFIG_PATH, 'w+')
        if not os.path.exists(DefaultSettings.LOG_DIR):
            os.makedirs(DefaultSettings.LOG_DIR)
        self.file = open(DefaultSettings.CONFIG_PATH, 'r+')
        try:
            self.settings = json.load(self.file)
        except json.decoder.JSONDecodeError:
            self.settings = {}
            self.settings['league_dir'] = DefaultSettings.LEAGUE_DIR
            self.settings['lobby'] = DefaultSettings.LOBBY
            self.settings['max_level'] = DefaultSettings.MAX_LEVEL
            self.settings['patch'] = DefaultSettings.PATCH
            self.settings['champs'] = DefaultSettings.CHAMPS
            self.settings['dialog'] = DefaultSettings.DIALOG
        try:
            r = requests.get('http://ddragon.leagueoflegends.com/api/versions.json')
            self.settings['patch'] = r.json()[0]
        except:
            pass
        self.set_league_dir(self.settings['league_dir'])

    def _json_update(self):
        self.file.seek(0)
        json.dump(self.settings, self.file, indent=4)
        self.file.truncate()

    def set_league_dir(self, _dir):
        self.settings['league_dir'] = _dir
        self.settings['league_path'] = os.path.join(_dir, 'LeagueClient')
        self.settings['league_config'] = os.path.join(_dir, 'Config/game.cfg')
        self.settings['league_lockfile'] = os.path.join(_dir, 'lockfile')
        self._json_update()

    def set_data(self, key, value):
        self.settings[key] = value
        self._json_update()

    def get_data(self, key):
        for sk, sv in self.settings.items():
            if sk == key:
                return self.settings[key]
