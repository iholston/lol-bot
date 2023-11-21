"""Configuration constants"""

import os

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

# PATHS
LEAGUE_CLIENT_DIR = "C:/Riot Games/League of Legends"
LEAGUE_CLIENT_PATH = LEAGUE_CLIENT_DIR + '/LeagueClient'
LEAGUE_GAME_CONFIG_PATH = LEAGUE_CLIENT_DIR + '/Config/game.cfg'
LEAGUE_CLIENT_LOCKFILE_PATH = LEAGUE_CLIENT_DIR + "/lockfile"
RIOT_CLIENT_LOCKFILE_PATH = os.getenv('LOCALAPPDATA') + '/Riot Games/Riot Client/Config/lockfile'
LOCAL_ACCOUNTS_PATH = os.getcwd() + "/lolbot/resources/accounts.json"
LOCAL_GAME_CONFIG_PATH = os.getcwd() + '/lolbot/resources/game.cfg'
LOCAL_APP_CONFIG_PATH = os.getcwd() + "/lolbot/resources/config.json"
LOCAL_ICON_PATH = os.getcwd() + '/lolbot/resources/images/a.ico'
LOCAL_LOG_PATH = os.getcwd() + '/logs'
if not os.path.exists(LOCAL_LOG_PATH):
    os.makedirs(LOCAL_LOG_PATH)

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
GAME_LOBBY_ID = 840
EARLY_GAME_END_TIME = 630
MAX_GAME_TIME = 2400
CHAMPS = [21, 18, 22, 67]
ASK_4_MID_DIALOG = ['mid ples',
                    'plannin on goin mid team',
                    'mid por favor',
                    'bienvenidos, mid',
                    'howdy, mid',
                    'goin mid',
                    'mid']
VERSION = 'v2.0.1'
