"""
View tab that handles bot controls and displays bot output
"""

import os
import multiprocessing
import requests
import threading
from time import sleep

import dearpygui.dearpygui as dpg

from lolbot.common import utils, api
from lolbot.common.config import ConfigRW
from lolbot.bot.client import Client


class BotTab:
    """Class that displays the BotTab and handles bot controls/output"""

    def __init__(self, message_queue: multiprocessing.Queue, terminate: threading.Event) -> None:
        self.message_queue = message_queue
        self.connection = api.Connection()
        self.lobbies = {
            'Draft Pick': 400,
            'Ranked Solo/Duo': 420,
            'Blind Pick': 430,
            'Ranked Flex': 440,
            'ARAM': 450,
            'Intro Bots': 830,
            'Beginner Bots': 840,
            'Intermediate Bots': 850,
            'Normal TFT': 1090,
            'Ranked TFT': 1100,
            'Hyper Roll TFT': 1130,
            'Double Up TFT': 1160
        }
        self.config = ConfigRW()
        self.terminate = terminate
        self.bot_thread = None

    def create_tab(self, parent) -> None:
        """Creates Bot Tab"""
        with dpg.tab(label="Bot", parent=parent) as self.status_tab:
            dpg.add_spacer()
            dpg.add_text(default_value="Controls")
            with dpg.group(horizontal=True):
                dpg.add_button(tag="StartButton", label='Start Bot', width=93, callback=self.start_bot)  # width=136
                dpg.add_button(label="Clear Output", width=93, callback=lambda: self.message_queue.put("Clear"))
                dpg.add_button(label="Restart UX", width=93, callback=self.ux_callback)
                dpg.add_button(label="Close Client", width=93, callback=self.close_client_callback)
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
            if not os.path.exists(self.config.get_data('league_dir')):
                self.message_queue.put("Clear")
                self.message_queue.put("League Installation Path is Invalid. Update Path to START")
                return
            self.message_queue.put("Clear")
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
            self.message_queue.put("Bot Successfully Terminated")

    def ux_callback(self) -> None:
        """Sends restart ux request to api"""
        if utils.is_league_running():
            self.connection.request('post', '/riotclient/kill-and-restart-ux')
            sleep(1)
            self.connection.set_lcu_headers()
        else:
            self.message_queue.put("Cannot restart UX, League is not running")

    def close_client_callback(self) -> None:
        """Closes all league related processes"""
        self.message_queue.put('Closing League Processes')
        threading.Thread(target=utils.close_all_processes).start()

    def update_info_panel(self) -> None:
        """Updates info panel text"""
        if not self.terminate.is_set() and not utils.is_league_running():
            dpg.configure_item("Info", default_value="League is not running")
        else:
            if not self.terminate.is_set() and not os.path.exists(self.config.get_data('league_dir')):
                self.message_queue.put("Clear")
                self.message_queue.put("League Installation Path is Invalid. Update Path")
                if not self.terminate.is_set():
                    threading.Timer(2, self.update_info_panel).start()
                else:
                    self.stop_bot()
                return

            _account = ""
            phase = ""
            league_patch = ""
            game_time = ""
            champ = ""
            level = ""
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
                        r = self.connection.request('get', '/lol-lobby/v2/lobby')
                        for lobby, id in self.lobbies.items():
                            if id == r.json()['gameConfig']['queueId']:
                                phase = lobby + ' Lobby'
            except:
                try:
                    self.connection.set_lcu_headers()
                except:
                    pass
            if utils.is_game_running() or phase == "InProgress":
                try:
                    response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', timeout=10, verify=False)
                    if response.status_code == 200:
                        for player in response.json()['allPlayers']:
                            if player['summonerName'] == response.json()['activePlayer']['summonerName']:
                                champ = player['championName']
                        game_time = utils.seconds_to_min_sec(response.json()['gameData']['gameTime'])
                except:
                    try:
                        self.connection.set_lcu_headers()
                    except:
                        pass
                msg = "Accnt: {}\n".format(_account)
                msg = msg + "Phase: {}\n".format(phase)
                msg = msg + "Time : {}\n".format(game_time)
                msg = msg + "Champ: {}\n".format(champ)
                msg = msg + "Level: {}".format(level)
            else:
                try:
                    r = requests.get('http://ddragon.leagueoflegends.com/api/versions.json')
                    league_patch = r.json()[0]
                except:
                    pass
                msg = "Accnt: {}\n".format(_account)
                msg = msg + "Phase: {}\n".format(phase)
                msg = msg + "Patch: {}\n".format(league_patch)
                msg = msg + "Level: {}".format(level)
            if not self.terminate.is_set():
                dpg.configure_item("Info", default_value=msg)

        if not self.terminate.is_set():
            threading.Timer(2, self.update_info_panel).start()
