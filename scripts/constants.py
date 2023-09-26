"""Configuration constants"""

import os
import logging

# COMMON - Configuration variables that you may need/want to change
# ---------------------------------------------------------------------------------------------------------

LEAGUE_CLIENT_DIR = 'C:/Riot Games/League of Legends'  # Path to your league installation. Make sure to use forward slashes
LOGGING_LEVEL = logging.INFO  # Change to logging.DEBUG if you are having issues with the bot
GAME_LOBBY_ID = 840  # Game mode. I recommend leaving it as beginner bots (840)
CHAMPS = [21, 18, 22, 67]  # Champ pick order. If the bot runs out of options it will just pick a random free-to-play champ
ASK_4_MID_DIALOG = [  # Champ select dialog. It randomly picks a dialog option to try and call mid
    "mid ples",
    "plannin on goin mid team",
    "mid por favor",
    "bienvenidos, mid",
    "howdy, mid",
    "goin mid",
    "mid"
]

# ---------------------------------------------------------------------------------------------------------

# PATHS
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
BEGINNER_BOTS_GAME_LOBBY_ID = 840
INTERMEDIATE_BOTS_GAME_LOBBY_ID = 850
EARLY_GAME_END_TIME = 630
MAX_GAME_TIME = 2400
STARTER_ITEMS_TO_BUY = 4
ITEMS_TO_BUY = 6

# GAME BUTTON RATIOS
GAME_ALL_ITEMS_RATIO = (0.4019, 0.2349)
GAME_BUY_STARTER_ITEM_RATIO = (0.2490, 0.3903)  # Based on the default shop open position on the all items tab
GAME_BUY_EPIC_ITEM_RATIO = (0.2519, 0.5923)  # Based on the default shop open position on the all items tab
GAME_BUY_LEGENDARY_ITEM_RATIO = (0.2875, 0.7571)
GAME_BUY_ITEM_RATIO_INCREASE = (.0366, 0)
GAME_BUY_PURCHASE_RATIO = (0.7644, 0.8216)  # Based on the default shop open position
GAME_MINI_MAP_UNDER_TURRET = (0.8760, 0.8846)
GAME_MINI_MAP_CENTER_MID = (0.8981, 0.8674)
GAME_MINI_MAP_ENEMY_NEXUS = (0.9628, 0.7852)
GAME_ULT_RATIO = (0.7298, 0.2689)
GAME_AFK_OK_RATIO = (0.4981, 0.4647)
GAME_CENTER_OF_SCREEN = (0.5, 0.5)
GAME_SYSTEM_MENU_X = (0.7729, 0.2488)

# CLIENT BUTTON RATIOS - ideally these would be unnecessary but idk the endpoints to clear rewards post game
POST_GAME_OK_RATIO = (0.4996, 0.9397)
POST_GAME_SELECT_CHAMP_RATIO = (0.4977, 0.5333)
POPUP_SEND_EMAIL_X_RATIO = (0.6960, 0.1238)

# RANDOM
MAX_CLIENT_ERRORS = 5
MAX_PHASE_ERRORS = 20
