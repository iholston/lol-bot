import os
import json

import requests


class Constants:
    pass


class Config:
    """Creates/updates configurations required by bot"""

    def __init__(self):
        """Ensures directories/files exist or creates them"""
        self.config_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'lolbot')
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.file_name = os.path.join(self.config_dir, 'config.json')
        if not os.path.exists(self.file_name):
            open(self.file_name, 'w+')
        self.file = open(self.file_name, 'r+')
        try:
            self.configs = json.load(self.file)
        except json.decoder.JSONDecodeError:
            self.configs = {'league_path': 'C:/Riot Games/League of Legends',
                            'lobby': 840,
                            'max_level': 30,
                            'champs': [21, 18, 22, 67],
                            'dialog': ["mid ples",
                                       "plannin on goin mid team",
                                       "mid por favor",
                                       "bienvenidos, mid",
                                       "howdy, mid",
                                       "goin mid",
                                       "mid"]
                            }
        try:
            r = requests.get('http://ddragon.leagueoflegends.com/api/versions.json')
            self.configs['patch'] = r.json()[0]
        except:
            self.configs['patch'] = '13.21.1'
        self._json_update()

    def _json_update(self):
        self.file.seek(0)
        json.dump(self.configs, self.file, indent=4)
        self.file.truncate()

    def set_data(self, key, value):
        self.configs[key] = value
        self._json_update()

    def get_data(self, key):
        for k, v in self.configs.items():
            if key == k:
                return self.configs[key]
