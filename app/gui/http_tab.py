import dearpygui.dearpygui as dpg
import webbrowser
import json
from ..common import api


class HTTPTab:

    def __init__(self):
        self.id = -1
        self.connection = api.Connection()
        self.methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    def create_tab(self, parent):
        with dpg.tab(label="HTTP", parent=parent) as self.id:
            with dpg.theme(tag="__demo_hyperlinkTheme"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 25])
                    dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])
            dpg.add_text("Method:")
            dpg.add_combo(tag='Method', items=self.methods, default_value='GET', width=569)
            dpg.add_text("URL:")
            dpg.add_input_text(tag='URL', width=568)
            dpg.add_text("Body:")
            dpg.add_input_text(tag='Body', width=568, height=45, multiline=True)
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Send Request", callback=self.request)
                dpg.add_button(label="Format JSON")
                dpg.add_spacer(width=110)
                dpg.add_text("Endpoints list: ")
                lcu = dpg.add_button(label="LCU", callback=lambda: webbrowser.open("https://lcu.kebs.dev/"))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open https://lcu.kebs.dev/ in webbrowser")
                dpg.bind_item_theme(lcu, "__demo_hyperlinkTheme")
                dpg.add_text("|")
                rcu = dpg.add_button(label="Riot Client", callback=lambda: webbrowser.open("https://riotclient.kebs.dev/"))
                with dpg.tooltip(dpg.last_item()):
                    dpg.add_text("Open https://riotclient.kebs.dev/ in webbrowser")
                dpg.bind_item_theme(rcu, "__demo_hyperlinkTheme")
            dpg.add_spacer()
            with dpg.group(horizontal=True):
                dpg.add_text("Response:")
                dpg.add_button(tag='StatusOutput', width=50)
                dpg.add_button(label="Copy to Clipboard")
            dpg.add_input_text(tag='ResponseOutput', width=568, height=124, multiline=True)

    def request(self):
        self.connection.set_lcu_headers()
        r = self.connection.request(dpg.get_value('Method').lower(), dpg.get_value('URL'), data=dpg.get_value('Body'))
        dpg.configure_item('StatusOutput', label=r.status_code)
        dpg.configure_item('ResponseOutput', default_value=json.dumps(r.json(), indent=4))
