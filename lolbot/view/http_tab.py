"""
View tab that sends custom HTTP requests to LCU API.
"""

import webbrowser
import json
import subprocess

import dearpygui.dearpygui as dpg

from lolbot.lcu.league_client import LeagueClient
class HTTPTab:
    """Class that displays the HTTPTab and sends custom HTTP requests to the LCU API"""

    def __init__(self, api: LeagueClient) -> None:
        self.id = -1
        self.api = api

    def create_tab(self, parent: int) -> None:
        """Creates the HTTPTab"""
        with dpg.tab(label="HTTP", parent=parent) as self.id:
            dpg.add_text("Method:")
            dpg.add_combo(tag='Method', items=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], default_value='GET', width=569)
            dpg.add_text("URL:")
            dpg.add_input_text(tag='URL', width=568)
            dpg.add_text("Body:")
            dpg.add_input_text(tag='Body', width=568, height=45, multiline=True)
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Send Request", callback=self.request)
                dpg.add_button(label="Format JSON", callback=self.format_json)
                dpg.add_spacer(width=110)
                dpg.add_text("Endpoints list: ")
                lcu = dpg.add_button(label="LCU", callback=lambda: webbrowser.open("https://lcu.kebs.dev/"))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open https://lcu.kebs.dev/ in webbrowser")
                dpg.bind_item_theme(lcu, "__hyperlinkTheme")
                dpg.add_text("|")
                rcu = dpg.add_button(label="Riot Client", callback=lambda: webbrowser.open("https://riotclient.kebs.dev/"))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open https://riotclient.kebs.dev/ in webbrowser")
                dpg.bind_item_theme(rcu, "__hyperlinkTheme")
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_text("Response:")
                dpg.add_button(tag='StatusOutput', width=50)
                dpg.add_button(label="Copy to Clipboard", callback=lambda: subprocess.run("pbcopy", text=True, input=dpg.get_value('ResponseOutput')))
            dpg.add_input_text(tag='ResponseOutput', width=568, height=124, multiline=True)

    @staticmethod
    def format_json() -> None:
        """Formats JSON text in the Body Text Field"""
        json_obj = None
        try:
            body = dpg.get_value('Body')
            if body[0] == "'" or body[0] == '"':
                body = body[1:]
            if body[len(body)-1] == "'" or body[len(body)-1] == '"':
                body = body[:-1]
            json_obj = json.loads(body)
        except Exception as e:
            dpg.set_value('Body', e)
        if json_obj is not None:
            dpg.set_value('Body', json.dumps(json_obj, indent=4))

    def request(self) -> None:
        """Sends custom HTTP request to LCU API"""
        try:
            response = None
            url = dpg.get_value('URL').strip()
            body = dpg.get_value('Body').strip()
            match dpg.get_value('Method').lower():
                case 'get':
                    response = self.api.make_get_request(url)
                case 'post':
                    response = self.api.make_post_request(url, body)
                case 'delete':
                    response = self.api.make_delete_request(url, body)
                case 'put':
                    response = self.api.make_put_request(url, body)
                case 'patch':
                    response = self.api.make_patch_request(url, body)
            dpg.configure_item('StatusOutput', label=response.status_code)
            dpg.configure_item('ResponseOutput', default_value=json.dumps(response.json(), indent=4))
        except Exception as e:
            dpg.configure_item('StatusOutput', label='418')
            dpg.configure_item('ResponseOutput', default_value=str(e))
