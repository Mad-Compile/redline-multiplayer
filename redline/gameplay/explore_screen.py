"""Playable top-down exploration prototype for REDLINE MAP 01."""
from __future__ import annotations

from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from redline.gameplay.map_data import load_map_layout

TILE = 10
WORLD_W = 128 * TILE
WORLD_H = 100 * TILE
MOVE_SPEED = 190.0


class ExploreWorld(Widget):
    """A lightweight 2D map renderer with a player-follow camera."""

    def __init__(self, layout, **kwargs):
        super().__init__(**kwargs)
        self.layout_data = layout
        self.player_x = 60 * TILE
        self.player_y = 50 * TILE
        self.direction = [0, 0]
        self.camera_x = 0
        self.camera_y = 0
        self._draw()
        self._clock = Clock.schedule_interval(self._update, 1 / 30)

    def set_direction(self, axis, value):
        self.direction[axis] = value

    def _update(self, dt):
        dx, dy = self.direction
        length = (dx * dx + dy * dy) ** 0.5
        if length:
            self.player_x += (dx / length) * MOVE_SPEED * min(dt, 0.05)
            self.player_y += (dy / length) * MOVE_SPEED * min(dt, 0.05)
            self.player_x = max(14, min(WORLD_W - 14, self.player_x))
            self.player_y = max(14, min(WORLD_H - 14, self.player_y))
        self.camera_x = max(0, min(WORLD_W - self.width,
                                   self.player_x - self.width / 2))
        self.camera_y = max(0, min(WORLD_H - self.height,
                                   self.player_y - self.height / 2))
        self._draw()

    def _screen(self, x, y):
        return self.x + x - self.camera_x, self.y + y - self.camera_y

    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.10, 0.13, 0.12, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Zone ground colours preserve the four areas in the supplied map.
            for key, zone in self.layout_data["zones"].items():
                x = zone["x1"] * TILE
                y = (100 - zone["y2"]) * TILE
                w = (zone["x2"] - zone["x1"]) * TILE
                h = (zone["y2"] - zone["y1"]) * TILE
                sx, sy = self._screen(x, y)
                colours = {
                    "A": (0.20, 0.105, 0.095, 1),
                    "B": (0.22, 0.16, 0.14, 1),
                    "C": (0.105, 0.19, 0.12, 1),
                    "D": (0.10, 0.15, 0.22, 1),
                }
                Color(*colours.get(key, (0.16, 0.16, 0.16, 1)))
                Rectangle(pos=(sx, sy), size=(w, h))

            # Main roads and rail corridor.
            Color(0.30, 0.30, 0.29, 1)
            for row in (2, 10, 18):
                sy = self._screen(0, (100 - row) * TILE)[1]
                Rectangle(pos=(self.x - self.camera_x, sy - dp(5)),
                          size=(WORLD_W, dp(10)))
            for col in (8, 24, 40, 70, 90, 110):
                sx = self._screen(col * TILE, 0)[0]
                Rectangle(pos=(sx - dp(5), self.y - self.camera_y),
                          size=(dp(10), WORLD_H))

            # Location buildings are drawn from the actual source tile bounds.
            for scene in self.layout_data["scenes"]:
                x = scene["tile_x"] * TILE
                y = (100 - scene["tile_y"] - scene["tile_h"]) * TILE
                w = scene["tile_w"] * TILE
                h = scene["tile_h"] * TILE
                sx, sy = self._screen(x, y)
                Color(0.075, 0.08, 0.085, 1)
                RoundedRectangle(pos=(sx, sy), size=(w, h), radius=[dp(3)])
                Color(0.42, 0.40, 0.36, 1)
                LineRect = Rectangle
                # Thin inset floor gives rooms a readable top-down footprint.
                Rectangle(pos=(sx + 2, sy + 2),
                          size=(max(1, w - 4), max(1, h - 4)))
                Color(0.18, 0.20, 0.19, 1)
                Rectangle(pos=(sx + 4, sy + 4),
                          size=(max(1, w - 8), max(1, h - 8)))

            # Player shadow, backpack, jacket and head: simple original 2D survivor.
            px, py = self._screen(self.player_x, self.player_y)
            Color(0, 0, 0, 0.35)
            Ellipse(pos=(px - dp(11), py - dp(9)), size=(dp(22), dp(12)))
            Color(0.32, 0.20, 0.12, 1)
            RoundedRectangle(pos=(px - dp(11), py - dp(7)),
                             size=(dp(7), dp(15)), radius=[dp(2)])
            Color(0.72, 0.12, 0.10, 1)
            RoundedRectangle(pos=(px - dp(7), py - dp(10)),
                             size=(dp(14), dp(19)), radius=[dp(4)])
            Color(0.83, 0.67, 0.50, 1)
            Ellipse(pos=(px - dp(6), py + dp(7)), size=(dp(12), dp(12)))
            Color(0.10, 0.10, 0.10, 1)
            Rectangle(pos=(px - dp(6), py + dp(15)),
                      size=(dp(12), dp(3)))

    def on_size(self, *_):
        self._draw()

    def on_pos(self, *_):
        self._draw()

    def on_parent(self, *_):
        if self.parent is None and hasattr(self, "_clock"):
            self._clock.cancel()


class ExploreScreen(BoxLayout):
    """Playable free-roam map mode with touch movement buttons."""

    def __init__(self, on_back, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(5),
                         padding=dp(8), **kwargs)
        self.on_back = on_back
        layout = load_map_layout()

        header = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        title = Label(text="REDLINE  /  MAP 01 EXPLORATION",
                      bold=True, halign="left", valign="middle")
        title.bind(size=lambda w, s: setattr(w, "text_size", s))
        header.add_widget(title)
        back = Button(text="MENU", size_hint_x=None, width=dp(82))
        back.bind(on_release=lambda *_: self.on_back())
        header.add_widget(back)
        self.add_widget(header)

        self.world = ExploreWorld(layout, size_hint=(1, 1))
        self.add_widget(self.world)

        controls = BoxLayout(size_hint_y=None, height=dp(112), spacing=dp(6))
        controls.add_widget(Label(text="MOVE", size_hint_x=0.65,
                                  bold=True, color=(0.8, 0.8, 0.8, 1)))
        pad = BoxLayout(orientation="vertical", spacing=dp(3))
        middle = BoxLayout(spacing=dp(3))
        up = Button(text="▲")
        down = Button(text="▼")
        left = Button(text="◀")
        right = Button(text="▶")
        middle.add_widget(left)
        middle.add_widget(up)
        middle.add_widget(right)
        pad.add_widget(middle)
        pad.add_widget(down)
        controls.add_widget(pad)
        self.add_widget(controls)

        # Buttons are hold-to-move; releasing always stops that direction.
        up.bind(on_press=lambda *_: self.world.set_direction(1, 1),
                on_release=lambda *_: self.world.set_direction(1, 0))
        down.bind(on_press=lambda *_: self.world.set_direction(1, -1),
                  on_release=lambda *_: self.world.set_direction(1, 0))
        left.bind(on_press=lambda *_: self.world.set_direction(0, -1),
                  on_release=lambda *_: self.world.set_direction(0, 0))
        right.bind(on_press=lambda *_: self.world.set_direction(0, 1),
                   on_release=lambda *_: self.world.set_direction(0, 0))
