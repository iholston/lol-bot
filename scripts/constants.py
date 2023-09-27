"""Configuration constants"""

import os
import logging

# PATHS
LEAGUE_CLIENT_DIR = 'C:/Riot Games/League of Legends'  # Path to your league installation. Make sure to use forward slashes
LEAGUE_CLIENT_PATH = LEAGUE_CLIENT_DIR + '/LeagueClient'
LEAGUE_CLIENT_LOCKFILE_PATH = LEAGUE_CLIENT_DIR + "/lockfile"
LEAGUE_GAME_CONFIG_PATH = LEAGUE_CLIENT_DIR + '/Config/game.cfg'
LOCAL_GAME_CONFIG_PATH = os.path.dirname(os.getcwd()) + '/resources/game.cfg'
RIOT_CLIENT_LOCKFILE_PATH = os.getenv('LOCALAPPDATA') + '/Riot Games/Riot Client/Config/lockfile'

# API INFO
LCU_HOST = '127.0.0.1'
RCU_HOST = '127.0.0.1'
LCU_USERNAME = 'riot'
RCU_USERNAME = 'riot'

# WINDOW NAMES
RIOT_CLIENT_WINNAME = "Riot Client Main"
LEAGUE_CLIENT_WINNAME = "League of Legends"
LEAGUE_GAME_CLIENT_WINNAME = "League of Legends (TM) Client"

# PROCESS NAMES
LEAGUE_PROCESS_NAMES = ["LeagueClient.exe", "League of Legends.exe"]
RIOT_CLIENT_PROCESS_NAMES = ["RiotClientUx.exe"]

# COMMANDS
KILL_LEAGUE_CLIENT = 'TASKKILL /F /IM LeagueClient.exe'
KILL_LEAGUE = 'TASKKILL /F /IM "League of Legends.exe"'
KILL_RIOT_CLIENT = 'TASKKILL /F /IM RiotClientUx.exe'

# GAME DATA
ACCOUNT_MAX_LEVEL = 30
GAME_LOBBY_ID = 840  # Game mode. I recommend leaving it as beginner bots (840)
EARLY_GAME_END_TIME = 630
MAX_GAME_TIME = 2400
CHAMPS = [21, 18, 22, 67]
ASK_4_MID_DIALOG = ["mid ples",
                    "plannin on goin mid team",
                    "mid por favor",
                    "bienvenidos, mid",
                    "howdy, mid",
                    "goin mid",
                    "mid"]

# ITEMS
STARTER_ITEMS = ["Cull",
                 "Doran's Blade",
                 "Doran's Ring",
                 "Doran's Shield"]

BOOTS = ["Berserker's Greaves",
         "Boots of Swiftness",
         "Ionian Boots of Lucidity",
         "Mercury's Treads",
         "Mobility Boots",
         "Plated Steelcaps",
         "Sorcerer's Shoes"]

LEGENDARY_ITEMS = [["Caulfield's Warhammer", "Pickaxe", "Kindlegem", "Spear of Shojin"],
                   ["Zeal", "Kircheis Shard", "Rapid Firecannon"],
                   ["Pickaxe", "Chain Vest", "Caulfield's Warhammer", "Death's Dance"],
                   ["Hearthbound Axe", "Zeal", "Phantom Dancer"],
                   ["Noonquiver", "Cloak of Agility", "Kircheis Shard", "Statikk Shiv"],
                   ["Vampiric Scepter", "Recurve Bow", "Pickaxe", "Blade of the Ruined King"]]

MYTHIC_ITEMS = [["Sheen", "Hearthbound Axe", "Kindlegem", "Trinity Force"],
                ["Serrated Dirk", "Caulfield's Warhammer", "Duskblade of Draktharr"],
                ["Caulfield's Warhammer", "B. F. Sword", "Cloak of Agility", "Navori Quickblades"],
                ["B. F. Sword", "Pickaxe", "Cloak of Agility", "Infinity Edge"],
                ["Aegis of the Legion", "Kindlegem", "Ruby Crystal"]]


# GAME BUTTON RATIOS
GAME_MINI_MAP_UNDER_TURRET = (0.8760, 0.8846)
GAME_MINI_MAP_CENTER_MID = (0.8981, 0.8674)
GAME_MINI_MAP_ENEMY_NEXUS = (0.9628, 0.7852)
GAME_ULT_RATIO = (0.7298, 0.2689)
GAME_AFK_OK_RATIO = (0.4981, 0.4647)
GAME_CENTER_OF_SCREEN = (0.5, 0.5)
GAME_SYSTEM_MENU_X = (0.7729, 0.2488)

# CLIENT BUTTON RATIOS
POST_GAME_OK_RATIO = (0.4996, 0.9397)
POST_GAME_SELECT_CHAMP_RATIO = (0.4977, 0.5333)
POPUP_SEND_EMAIL_X_RATIO = (0.6960, 0.1238)

# RANDOM
LOGGING_LEVEL = logging.INFO  # Change to logging.DEBUG if you are having issues with the bot
MAX_CLIENT_ERRORS = 5
MAX_PHASE_ERRORS = 20
