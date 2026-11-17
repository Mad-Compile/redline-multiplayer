"""Interactive location browser for the user-supplied REDLINE MAP 01 schematic.

This screen uses the map package's actual tile coordinates and room metadata.
It is a map/layout browser, not a claim that the environment art or character
gameplay is finished.
"""
from __future__ import annotations

from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from redline.gameplay.map_data import load_map_layout


TILE_PX = 14
MAP_WIDTH = 128 * TILE_PX
MAP_HEIGHT = 100 * TILE_PX

ZONE_COLOURS = {
    "A": (0.30, 0.075, 0.075, 1),
    "B": (0.34, 0.055, 0.055, 1),
    "C": (0.075, 0.25, 0.105, 1),
    "D": (0.075, 0.11, 0.31, 1),
}
ROOM_COLOURS = {
    "A": (0.23, 0.065, 0.065, 1),
    "B": (0.42, 0.075, 0.075, 1),
    "C": (0.065, 0.19, 0.085, 1),
    "D": (0.07, 0.095, 0.25, 1),
}
ZONE_NAMES = {
    "A": "ZOMBIE TERRITORY",
    "B": "CENTRAL SECURITY WALL",
    "C": "SURVIVOR TERRITORY",
    "D": "TRAIN ESCAPE STATION",
}


class MapSchematic(Widget):
    """Scrollable map assembled from the exact supplied tile/room coordinates."""

    def __init__(self, layout, on_scene, **kwargs):
        super().__init__(size_hint=(None, None), size=(MAP_WIDTH, MAP_HEIGHT), **kwargs)
        self.layout_data = layout
        self.on_scene = on_scene
        self._draw_base()
        self._add_locations()

    def _tile_position(self, tile_x, tile_y, tile_w, tile_h):
        x = tile_x * TILE_PX
        y = (100 - tile_y - tile_h) * TILE_PX
        return x, y, tile_w * TILE_PX, tile_h * TILE_PX

    def _draw_base(self):
        with self.canvas.before:
            Color(0.025, 0.03, 0.035, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Four territories retain the uploaded map's tile boundaries.
            for key, zone in self.layout_data["zones"].items():
                x = zone["x1"] * TILE_PX
                y = (100 - zone["y2"]) * TILE_PX
                w = (zone["x2"] - zone["x1"]) * TILE_PX
                h = (zone["y2"] - zone["y1"]) * TILE_PX
                Color(*ZONE_COLOURS[key])
                Rectangle(pos=(x, y), size=(w, h))

            # Map road axes follow the user's renderer's tile-row/column scheme.
            Color(0.19, 0.19, 0.19, 1)
            road_width = dp(7)
            for row in (2, 10, 18):
                y = (100 - row) * TILE_PX
                Rectangle(pos=(0, y - road_width / 2),
                          size=(48 * TILE_PX, road_width))
            for col in (8, 24, 40):
                x = col * TILE_PX
                Rectangle(pos=(x - road_width / 2, (100 - 72) * TILE_PX),
                          size=(road_width, 72 * TILE_PX))
            for row in (10, 20, 30):
                y = (100 - row) * TILE_PX
                Rectangle(pos=(54 * TILE_PX, y - road_width / 2),
                          size=(74 * TILE_PX, road_width))
            for col in (70, 90, 110):
                x = col * TILE_PX
                Rectangle(pos=(x - road_width / 2, (100 - 72) * TILE_PX),
                          size=(road_width, 72 * TILE_PX))

            # Tile grid, deliberately subtle like the supplied overview.
            Color(0.56, 0.58, 0.60, 0.18)
            for col in range(129):
                x = col * TILE_PX
                Line(points=(x, 0, x, MAP_HEIGHT), width=0.45)
            for row in range(101):
                y = row * TILE_PX
                Line(points=(0, y, MAP_WIDTH, y), width=0.45)

    def _add_locations(self):
        for scene in self.layout_data["scenes"]:
            x, y, w, h = self._tile_position(
                scene["tile_x"], scene["tile_y"], scene["tile_w"], scene["tile_h"]
            )
            title = scene["name"]
            spawn = scene.get("spawn")
            if spawn:
                title += "\n" + ("ZOMBIE SPAWN" if spawn == "zombie" else "SURVIVOR SPAWN")
            if scene.get("objective"):
                title += "\n★ OBJECTIVE"

            button = Button(
                text=title,
                size_hint=(None, None),
                size=(w, h),
                pos=(x, y),
                background_normal="",
                background_down="",
                background_color=ROOM_COLOURS[scene["zone"]],
                color=(0.96, 0.94, 0.89, 1),
                font_size="9sp",
                halign="center",
                valign="middle",
                padding=(dp(3), dp(2)),
            )
            button.text_size = (max(8, w - dp(6)), max(8, h - dp(4)))
            button.bind(on_release=lambda _button, selected=scene: self.on_scene(selected))
            self.add_widget(button)


class MapScreen(BoxLayout):
    def __init__(self, on_back, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(5), padding=dp(8), **kwargs)
        self.on_back = on_back
        self.layout_data = load_map_layout()

        with self.canvas.before:
            Color(0.025, 0.035, 0.045, 1)
            self._background = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_background, size=self._update_background)

        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(46), spacing=dp(8))
        title = Label(text="REDLINE  /  MAP 01: TRAIN ESCAPE",
                      bold=True, halign="left", valign="middle")
        title.bind(size=lambda instance, size: setattr(instance, "text_size", size))
        header.add_widget(title)
        back = Button(text="BACK", size_hint_x=None, width=dp(90))
        back.bind(on_release=lambda *_: self.on_back())
        header.add_widget(back)
        self.add_widget(header)

        self.map_view = ScrollView(
            do_scroll_x=True, do_scroll_y=True,
            bar_width=dp(5), scroll_type=["bars", "content"],
        )
        self.map_canvas = MapSchematic(self.layout_data, self._show_scene)
        self.map_view.add_widget(self.map_canvas)
        self.add_widget(self.map_view)

        footer = Label(
            text="MAP SCHEMATIC  •  4 ZONES  •  39 LOCATIONS  •  TAP A ROOM FOR DETAILS\n"
                 "Layout reference only — not finished walkable environment art",
            size_hint_y=None, height=dp(42), font_size="11sp",
            halign="center", valign="middle",
        )
        footer.bind(size=lambda instance, size: setattr(instance, "text_size", size))
        self.add_widget(footer)

    def _update_background(self, *_):
        self._background.pos = self.pos
        self._background.size = self.size

    def _show_scene(self, scene):
        zone_name = ZONE_NAMES.get(scene.get("zone"), "UNKNOWN ZONE")
        loot = scene.get("loot", [])
        loot_text = "\n".join(
            f"• {item['item'].replace('_', ' ').upper()} ×{item['qty']}"
            for item in loot
        ) or "No loot listed"
        exits = scene.get("exits", scene.get("connects", []))
        exits_text = ", ".join(item.replace("_", " ").upper() for item in exits) or "None listed"
        objective = scene.get("objective")
        details = [
            zone_name,
            "",
            scene.get("description", ""),
            "",
            f"LOOT\n{loot_text}",
            "",
            f"OBJECTIVE\n{objective.replace('_', ' ').upper() if objective else 'No objective assigned'}",
            "",
            f"CONNECTIONS\n{exits_text}",
        ]
        if scene.get("spawn"):
            details.extend(["", "SPAWN: " + scene["spawn"].upper()])

        body = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        label = Label(text="\n".join(details), halign="left", valign="top")
        label.bind(size=lambda instance, size: setattr(instance, "text_size", size))
        body.add_widget(label)
        close = Button(text="CLOSE", size_hint_y=None, height=dp(42))
        body.add_widget(close)
        popup = Popup(
            title=scene["name"],
            content=body,
            size_hint=(0.82, 0.78),
            auto_dismiss=True,
        )
        close.bind(on_release=popup.dismiss)
        popup.open()
