"""
View tab that shows live mouse coordinates and window-relative ratios.
"""

from pynput import mouse
import dearpygui.dearpygui as dpg
from Quartz import CGEventCreate, CGEventGetLocation

from lolbot.system import window


class CoordinatesTab:
    """Displays live cursor coordinates and window ratios."""

    def __init__(self) -> None:
        self.id = None
        self.mouse_down = False
        self.last_saved = "-"
        self.last_client_ratio = "-"
        self.listener = mouse.Listener(on_click=self._on_click)
        self.listener.daemon = True
        self.listener.start()

    def create_tab(self, parent: int) -> None:
        with dpg.tab(label="Coordinates", parent=parent) as self.id:
            dpg.add_text("Live Cursor Position")
            dpg.add_spacer()

            dpg.add_text("Screen (px):")
            dpg.add_input_text(tag="CoordScreen", readonly=True, width=560)

            dpg.add_spacer()
            dpg.add_text("Client window ratio:")
            dpg.add_input_text(tag="CoordClientRatio", readonly=True, width=560)
            dpg.add_input_text(tag="CoordClientWindow", readonly=True, width=560)

            dpg.add_spacer()
            dpg.add_text("Game window ratio:")
            dpg.add_input_text(tag="CoordGameRatio", readonly=True, width=560)
            dpg.add_input_text(tag="CoordGameWindow", readonly=True, width=560)

            dpg.add_spacer()
            dpg.add_text("Last saved ratio (right-click to save):")
            dpg.add_input_text(tag="CoordLastSaved", readonly=True, width=560)

    def update_panel(self) -> None:
        if self.mouse_down:
            return
        point = CGEventGetLocation(CGEventCreate(None))
        x, y = float(point.x), float(point.y)
        dpg.set_value("CoordScreen", f"({x:.1f}, {y:.1f})")

        client_ratio, client_window = self._get_ratio_details(
            x, y, window.CLIENT_WINDOW
        )
        game_ratio, game_window = self._get_ratio_details(
            x, y, window.GAME_WINDOW
        )

        dpg.set_value("CoordClientRatio", client_ratio)
        dpg.set_value("CoordClientWindow", client_window)
        self.last_client_ratio = client_ratio

        dpg.set_value("CoordGameRatio", game_ratio)
        dpg.set_value("CoordGameWindow", game_window)
        dpg.set_value("CoordLastSaved", self.last_saved)

    @staticmethod
    def _get_ratio_details(
        x: float,
        y: float,
        window_name: str,
    ) -> tuple[str, str]:
        try:
            win_x, win_y, width, height = window.get_window_size(window_name)
        except window.WindowNotFound:
            return "-", "-"
        if width == 0 or height == 0:
            return "-", "-"

        window_text = f"x: {win_x}, y: {win_y}, width: {width}, height: {height}"

        if x < win_x or y < win_y or x > win_x + width or y > win_y + height:
            return "-", window_text
        ratio_x = (x - win_x) / width
        ratio_y = (y - win_y) / height
        ratio_text = f"({ratio_x:.4f}, {ratio_y:.4f})"
        return ratio_text, window_text

    def _on_click(self, _x, _y, button, pressed: bool) -> None:
        self.mouse_down = pressed
        if pressed and button == mouse.Button.right:
            if self.last_client_ratio and self.last_client_ratio != "-":
                dpg.set_clipboard_text(self.last_client_ratio)
                self.last_saved = self.last_client_ratio