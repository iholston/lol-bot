"""
View tab that handles bot controls and displays bot output
"""

import os
import multiprocessing
import threading
import time
import datetime

import dearpygui.dearpygui as dpg

from lolbot.common import config, proc
from lolbot.lcu import lcu_api, game_api
from lolbot.bot.bot import Bot


class BotTab:
    """Class that displays the BotTab and handles bot controls/output"""

    def __init__(self):
        self.message_queue = multiprocessing.Queue()
        self.games_played = multiprocessing.Value('i', 0)
        self.bot_errors = multiprocessing.Value('i', 0)
        self.api = lcu_api.LCUApi()
        self.api.update_auth_timer()
        self.output_queue = []
        self.endpoint = None
        self.bot_thread = None
        self.start_time = None

    def create_tab(self, parent) -> None:
        """Creates Bot Tab"""
        with dpg.tab(label="Bot", parent=parent) as self.status_tab:
            dpg.add_spacer()
            dpg.add_text(default_value="Controls")
            with dpg.group(horizontal=True):
                dpg.add_button(tag="StartButton", label='Start Bot', width=93, callback=self.start_bot)  # width=136
                dpg.add_button(label="Clear Output", width=93, callback=lambda: self.message_queue.put("Clear"))
                dpg.add_button(label="Restart UX", width=93, callback=self.restart_ux)
                dpg.add_button(label="Close Client", width=93, callback=self.close_client)
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text(default_value="Info")
                    dpg.add_input_text(tag="Info", readonly=True, multiline=True, default_value="Initializing...", height=72, width=280, tab_input=True)
                with dpg.group():
                    dpg.add_text(default_value="Bot")
                    dpg.add_input_text(tag="Bot", readonly=True, multiline=True, default_value="Initializing...", height=72, width=280, tab_input=True)
            dpg.add_spacer()
            dpg.add_text(default_value="Output")
            dpg.add_input_text(tag="Output", multiline=True, default_value="", height=162, width=568, enabled=False)

        # Start self updating
        self.update_info_panel()
        self.update_bot_panel()
        self.update_output_panel()

    def start_bot(self) -> None:
        """Starts bot process"""
        if self.bot_thread is None:
            if not os.path.exists(config.load_config()['league_dir']):
                self.message_queue.put("Clear")
                self.message_queue.put("League Installation Path is Invalid. Update Path to START")
                return
            self.message_queue.put("Clear")
            self.start_time = time.time()
            bot = Bot()

            self.bot_thread = multiprocessing.Process(target=bot.run, args=(self.message_queue,))
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

    def restart_ux(self) -> None:
        """Sends restart ux request to api"""
        if not proc.is_league_running():
            self.message_queue.put("Cannot restart UX, League is not running")
            return
        try:
            self.api.restart_ux()
        except:
            pass

    def close_client(self) -> None:
        """Closes all league related processes"""
        self.message_queue.put('Closing League Processes')
        threading.Thread(target=proc.close_all_processes).start()

    def update_info_panel(self) -> None:
        """Updates info panel text continuously"""
        threading.Timer(2, self.update_info_panel).start()

        if not proc.is_league_running():
            msg = "Accnt: -\nLevel: -\nPhase: Closed\nTime : -\nChamp: -"
            dpg.configure_item("Info", default_value=msg)
            return

        try:
            account = self.api.get_display_name()
            level = self.api.get_summoner_level()
            phase = self.api.get_phase()

            msg = f"Accnt: {account}\n"
            if phase == "None":
                msg += "Phase: In Main Menu\n"
            elif phase == "Matchmaking":
                msg += "Phase: In Queue\n"
            elif phase == "Lobby":
                lobby_id = self.api.get_lobby_id()
                for lobby, id in config.LOBBIES.items():
                    if id == lobby_id:
                        phase = lobby + " Lobby"
                msg += f"Phase: {phase}\n"
            elif phase == "InProgress":
                msg += "Phase: In Game\n"
            else:
                msg += f"Phase: {phase}"
            msg += f"Level: {level}\n"
            if phase == "InProgress":
                msg += f"Time : {game_api.get_formatted_time()}"
                msg += f"Champ: {game_api.get_champ()}"
            else:
                msg += "Time : -\n"
                msg += "Champ: -"
            dpg.configure_item("Info", default_value=msg)
        except:
            pass

    def update_bot_panel(self):
        threading.Timer(.5, self.update_bot_panel).start()
        msg = ""
        if self.bot_thread is None:
            msg += "Status : Ready\nRunTime: -\nGames  : -\nXP Gain: -\nErrors : -"
        else:
            msg += "Status : Running\n"
            run_time = datetime.timedelta(seconds=(time.time() - self.start_time))
            days = run_time.days
            hours, remainder = divmod(run_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if days > 0:
                msg += f"RunTime: {days} day, {hours:02}:{minutes:02}:{seconds:02}\n"
            else:
                msg += f"RunTime: {hours:02}:{minutes:02}:{seconds:02}\n"
            msg += f"Games  : {self.games_played.value}\n"
            try:
                msg += f"XP Gain: nah\n"
            except:
                msg += f"XP Gain: 0\n"
            msg += f"Errors : {self.bot_errors.value}"
        dpg.configure_item("Bot", default_value=msg)

    def update_output_panel(self):
        threading.Timer(.5, self.update_output_panel).start()
        if not self.message_queue.empty():
            display_msg = ""
            self.output_queue.append(self.message_queue.get())
            if len(self.output_queue) > 12:
                self.output_queue.pop(0)
            for msg in self.output_queue:
                if "Clear" in msg:
                    self.output_queue = []
                    display_msg = ""
                    break
                elif "INFO" not in msg and "ERROR" not in msg and "WARNING" not in msg:
                    display_msg += "[{}] [INFO   ] {}\n".format(datetime.datetime.now().strftime("%H:%M:%S"), msg)
                else:
                    display_msg += msg + "\n"
            dpg.configure_item("Output", default_value=display_msg.strip())
            if "Bot Successfully Terminated" in display_msg:
                self.output_queue = []
