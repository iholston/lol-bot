"""
View tab that handles bot controls and displays bot output.
"""

import multiprocessing
import os.path
import threading
import time
import datetime
import textwrap

import dearpygui.dearpygui as dpg

from lolbot.common import config
from lolbot.system import cmd
from lolbot.lcu.league_client import LeagueClient, LCUError
import lolbot.lcu.game_server as game_api
from lolbot.bot.bot import Bot


class BotTab:
    """Class that displays the BotTab and handles bot controls/output"""

    def __init__(self, api: LeagueClient):
        self.message_queue = multiprocessing.Queue()
        self.games_played = multiprocessing.Value('i', 0)
        self.bot_errors = multiprocessing.Value('i', 0)
        self.api = api
        self.output_queue = []
        self.endpoint = None
        self.bot_thread = None
        self.start_time = None

    def create_tab(self, parent) -> None:
        with dpg.tab(label="Bot", parent=parent) as self.status_tab:
            dpg.add_spacer()
            dpg.add_text(default_value="Controls")
            with dpg.group(horizontal=True):
                dpg.add_button(tag="StartStopButton", label='Start Bot', width=93, callback=self.start_stop_bot)
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

    def start_stop_bot(self) -> None:
        conf = config.load_config()
        if self.bot_thread is None:
            if os.path.exists(conf.windows_install_dir) or os.path.exists(conf.macos_install_dir):
                self.message_queue.put("Clear")
                self.start_time = time.time()
                self.bot_thread = multiprocessing.Process(target=Bot().run, args=(self.message_queue, self.games_played, self.bot_errors))
                self.bot_thread.start()
                dpg.configure_item("StartStopButton", label="Quit Bot")
                return
            self.message_queue.put("Clear")
            self.message_queue.put("League Installation Path is Invalid. Update Path to START")
        else:
            dpg.configure_item("StartStopButton", label="Start Bot")
            self.stop_bot()

    def stop_bot(self):
        if self.bot_thread is not None:
            self.bot_thread.terminate()
            self.bot_thread.join()
            self.bot_thread = None
            self.message_queue.put("Bot Successfully Terminated")

    def restart_ux(self) -> None:
        if not cmd.run(cmd.IS_CLIENT_RUNNING):
            self.message_queue.put("Cannot restart UX, League is not running")
            return
        try:
            self.api.restart_ux()
        except LCUError:
            pass

    def close_client(self) -> None:
        """Closes all league related processes"""
        self.message_queue.put('Closing League Processes')
        threading.Thread(target=cmd.run, args=(cmd.CLOSE_ALL,)).start()

    def update_info_panel(self) -> None:
        if not cmd.run(cmd.IS_CLIENT_RUNNING):
            msg = textwrap.dedent("""\
            Phase: Closed
            Accnt: -
            Level: -
            Time : -
            Champ: -""")
            dpg.configure_item("Info", default_value=msg)
            return
        try:
            phase = self.api.get_phase()
            game_time = "-"
            champ = "-"
            match phase:
                case "None":
                    phase = "In Main Menu"
                case "Matchmaking":
                    phase = "In Queue"
                    game_time = self.api.get_matchmaking_time()
                case "Lobby":
                    lobby_id = self.api.get_lobby_id()
                    for lobby, id in config.ALL_LOBBIES.items():
                        if id == lobby_id:
                            phase = lobby + " Lobby"
                case "ChampSelect":
                    game_time = self.api.get_cs_time_remaining()
                case "InProgress":
                    phase = "In Game"
                    try:
                        game_time = game_api.get_formatted_time()
                        champ = game_api.get_champ()
                    except:
                        pass
                case _:
                    pass
            msg = textwrap.dedent(f"""\
            Phase: {phase}
            Accnt: {self.api.get_summoner_name()}
            Level: {self.api.get_summoner_level()}
            Time : {game_time}
            Champ: {champ}""")
            dpg.configure_item("Info", default_value=msg)
        except LCUError:
            pass

    def update_bot_panel(self):
        msg = ""
        if self.bot_thread is None:
            msg += textwrap.dedent("""\
            Status : Ready
            RunTime: -
            Games  : -
            Errors : -
            Action : -""")
        else:
            run_time = datetime.timedelta(seconds=(time.time() - self.start_time))
            hours, remainder = divmod(run_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if run_time.days > 0:
                time_since_start = f"{run_time.days} day, {hours:02}:{minutes:02}:{seconds:02}"
            else:
                time_since_start = f"{hours:02}:{minutes:02}:{seconds:02}"
            if len(self.output_queue) > 0:
                action = f"{self.output_queue[-1].split(']')[-1].strip()}"
            else:
                action = "-"
            msg = textwrap.dedent(f"""\
            Status : Running
            RunTime: {time_since_start}
            Games  : {self.games_played.value}
            Errors : {self.bot_errors.value}
            Action : {action}""")
        dpg.configure_item("Bot", default_value=msg)

    def update_output_panel(self):
        """Updates output panel with latest log messages."""
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
                    display_msg += f'[{datetime.datetime.now().strftime("%H:%M:%S")}] [INFO   ] {msg}\n'
                else:
                    display_msg += msg + "\n"
            if "Bot Successfully Terminated" in display_msg:
                self.output_queue = []
            dpg.configure_item("Output", default_value=display_msg.strip())
