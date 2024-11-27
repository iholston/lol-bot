"""
Handles multi-platform creating/writing LoLBot's configurations to json file.
"""

import os
import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parents[3] / 'lolbot-settings'
BAK_DIR = os.path.join(CONFIG_DIR, 'bak')
LOG_DIR = os.path.join(CONFIG_DIR, 'logs')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
ACCOUNT_PATH = os.path.join(CONFIG_DIR, 'accounts.json')
ICON_PATH = 'assets/logo.ico'

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(BAK_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

ALL_LOBBIES = {
    'Draft Pick': 400,
    'Ranked Solo/Duo': 420,
    'Blind Pick': 430,
    'Ranked Flex': 440,
    'ARAM': 450,
    'Intro Bots': 870,
    'Beginner Bots': 880,
    'Intermediate Bots': 890,
    'Normal TFT': 1090,
    'Ranked TFT': 1100,
    'Hyper Roll TFT': 1130,
    'Double Up TFT': 1160
}

BOT_LOBBIES = {
    'Intro Bots': 870,
    'Beginner Bots': 880,
    'Intermediate Bots': 890,
}

FPS_OPTIONS = {
    "25": 3,
    "30": 4,
    "60": 5,
    "80": 6,
    "120": 7,
    "144": 8,
    "200": 9,
    "240": 2,
    "Uncapped": 10,
}


@dataclass
class Config:
    windows_install_dir: str = "C:/Riot Games/League of Legends"
    macos_install_dir: str = "/Applications/League of Legends.app"
    lobby: int = 880
    max_level: int = 30
    fps_type: int = FPS_OPTIONS.get("60")


def load_config() -> Config:
    if not os.path.exists(CONFIG_PATH):
        default_config = Config()
        save_config(default_config)
        return default_config
    try:
        with open(CONFIG_PATH, 'r') as configfile:
            data = json.load(configfile)
            return Config(**data)
    except json.JSONDecodeError:
        return Config()


def save_config(config: Config) -> None:
    with open(CONFIG_PATH, 'w') as configfile:
        json.dump(config.__dict__, configfile, indent=4)
