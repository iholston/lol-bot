import os
import json

import requests


CONFIG_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'lolbot')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
ACCOUNT_PATH = os.path.join(CONFIG_DIR, 'accounts.json')
RIOT_CLIENT_LOCKFILE_PATH = os.path.join(os.getenv('LOCALAPPDATA'), '/Riot Games/Riot Client/Config/lockfile')
LOCAL_GAME_CONFIG_PATH = os.path.join(os.getcwd(), '/lolbot/resources/game.cfg')
ICON_PATH = os.path.join(os.getcwd(), '/lolbot/resources/images/a.ico')
LOG_PATH = os.path.join(os.getcwd(), '/logs')
VERSION = '3.0.0'
DEFAULT_SETTINGS = {'league_dir': 'C:/Riot Games/League of Legends',
                    'lobby': 840,
                    'max_level': 30,
                    'champs': [21, 18, 22, 67],
                    'patch': '13.21.1',
                    'dialog': ["mid ples",
                               "plannin on goin mid team",
                               "mid por favor",
                               "bienvenidos, mid",
                               "howdy, mid",
                               "goin mid",
                               "mid"]
                    }

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w+') as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)
if not os.path.exists(ACCOUNT_PATH):
    with open(ACCOUNT_PATH, 'w+') as f:
        pass


class Config:
    """Creates/updates configurations required by bot"""

    def __init__(self):
        self.file = open(CONFIG_PATH, 'r+')
        try:
            self.settings = json.load(self.file)
        except:
            self.settings = DEFAULT_SETTINGS
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
        for k, v in self.settings.items():
            if key == k:
                return self.settings[key]
