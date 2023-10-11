import os
import multiprocessing
import requests
import threading
import dearpygui.dearpygui as dpg
from ..common import constants, utils, api
from ..bot.client import Client

class BotTab:

    def __init__(self, message_queue, terminate):
        self.message_queue = message_queue
        self.connection = api.Connection()
        self.terminate = terminate
        self.bot_thread = None

    def create_tab(self, parent):
        """Creates Status Tab"""
        with dpg.tab(label="Bot", parent=parent) as self.status_tab:
            dpg.add_spacer()
            dpg.add_text(default_value="Controls")
            with dpg.group(horizontal=True):
                dpg.add_button(tag="StartButton", label='Start Bot', width=90, callback=self.start_bot)
                dpg.add_button(label="Restart UX", width=90)
                dpg.add_button(label='Close Client', width=90)
            dpg.add_spacer()
            dpg.add_text(default_value="Info")
            dpg.add_input_text(tag="Info", readonly=True, multiline=True, default_value="Initializing...", height=72, width=568, tab_input=True)
            dpg.add_spacer()
            dpg.add_text(default_value="Output")
            dpg.add_input_text(tag="Output", multiline=True, default_value="", height=162, width=568, enabled=False)
        self.update_info_panel()

    def start_bot(self) -> None:
        """Starts bot process"""
        if self.bot_thread is None:
            if not os.path.exists(constants.LEAGUE_CLIENT_DIR):
                dpg.configure_item("Info", default_value="League Path is Invalid. Update Path to start bot")
                return
            self.bot_thread = multiprocessing.Process(target=Client, args=(self.message_queue,))
            self.bot_thread.start()
            dpg.configure_item("StartButton", label="Quit Bot")
        else:
            dpg.configure_item("StartButton", label="Start Bot")
            self.stop_bot()

    def stop_bot(self) -> None:
        """Stops bot process"""
        if self.bot_thread is not None:
            self.bot_thread.terminate()
            self.bot_thread.join()
            self.bot_thread = None
            self.message_queue.put("\nBot Successfully Terminated")

    def update_info_panel(self) -> None:
        """Updates gui info string"""
        if not utils.is_league_running():
            dpg.configure_item("Info", default_value="League is not running")
        else:
            _account = "Unknown"
            phase = "None"
            league_patch = "0.0.0"
            game_time = "-1"
            champ = "None"
            level = '-1'
            try:
                if not self.connection.headers:
                    self.connection.set_lcu_headers()
                r = self.connection.request('get', '/lol-summoner/v1/current-summoner')
                if r.status_code == 200:
                    _account = r.json()['displayName']
                    level = str(r.json()['summonerLevel']) + " - " + str(
                        r.json()['percentCompleteForNextLevel']) + "% to next level"
                r = self.connection.request('get', '/lol-gameflow/v1/gameflow-phase')
                if r.status_code == 200:
                    phase = r.json()
                    if phase == 'None':
                        phase = "In Main Menu"
                    elif phase == 'Matchmaking':
                        phase = 'In Queue'
                    elif phase == 'Lobby':
                        phase = '{Type} Lobby'
            except:
                pass
            if utils.is_game_running() or phase == "InProgress":
                try:
                    response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', timeout=10,
                                            verify=False)
                    if response.status_code == 200:
                        for player in response.json()['allPlayers']:
                            if player['summonerName'] == response.json()['activePlayer']['summonerName']:
                                champ = player['championName']
                        game_time = utils.seconds_to_min_sec(
                            response.json()['gameData']['gameTime'])
                except:
                    pass
                msg = "Account: {}\n".format(_account)
                msg = msg + "Status: {}\n".format(phase)
                msg = msg + "Game Time: {}\n".format(game_time)
                msg = msg + "Champ: {}\n".format(champ)
                msg = msg + "Level: {}".format(level)
            else:
                try:
                    r = requests.get('http://ddragon.leagueoflegends.com/api/versions.json')
                    league_patch = r.json()[0]
                except:
                    pass
                msg = "Account: {}\n".format(_account)
                msg = msg + "Status: {}\n".format(phase)
                msg = msg + "Patch: {}\n".format(league_patch)
                msg = msg + "Champ: {}\n".format(champ)
                msg = msg + "Level: {}".format(level)
            dpg.configure_item("Info", default_value=msg)

        if not self.terminate:
            threading.Timer(2, self.update_info_panel).start()