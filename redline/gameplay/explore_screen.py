"""Top-down REDLINE exploration using the supplied Train Escape map artwork."""
from __future__ import annotations

from pathlib import Path

from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget

from redline.gameplay.map_data import load_map_layout

# The supplied artwork is a 3:2 overview. Keep the game-world coordinate
# system at the original artwork's aspect ratio so scene tile positions map
# consistently onto the visible map.
WORLD_W = 1536.0
WORLD_H = 1024.0
MOVE_SPEED = 230.0
MAP_IMAGE_PATH = Path(__file__).resolve().parents[2] / "assets" / "maps" / "redline_train_escape.jpg"


class SurvivorSprite(Widget):
    """Simple original 2D survivor marker drawn above the supplied map."""

    def __init__(self, **kwargs):
        super().__init__(size_hint=(None, None), size=(dp(34), dp(42)), **kwargs)
        with self.canvas:
            Color(0, 0, 0, 0.48)
            self.shadow = Ellipse()
            Color(0.27, 0.18, 0.12, 1)
            self.backpack = RoundedRectangle(radius=[dp(3)])
            Color(0.72, 0.10, 0.10, 1)
            self.jacket = RoundedRectangle(radius=[dp(4)])
            Color(0.84, 0.68, 0.52, 1)
            self.head = Ellipse()
            Color(0.08, 0.08, 0.08, 1)
            self.hair = RoundedRectangle(radius=[dp(2)])
        self.bind(pos=self._layout, size=self._layout)
        self._layout()

    def _layout(self, *_):
        x, y = self.pos
        self.shadow.pos = (x + dp(5), y + dp(3))
        self.shadow.size = (dp(25), dp(11))
        self.backpack.pos = (x + dp(3), y + dp(10))
        self.backpack.size = (dp(10), dp(22))
        self.jacket.pos = (x + dp(9), y + dp(8))
        self.jacket.size = (dp(17), dp(24))
        self.head.pos = (x + dp(11), y + dp(27))
        self.head.size = (dp(13), dp(13))
        self.hair.pos = (x + dp(10), y + dp(37))
        self.hair.size = (dp(15), dp(4))


class ExploreWorld(StencilView):
    """Scrollable camera world whose background is the user's actual map image."""

    def __init__(self, layout, **kwargs):
        super().__init__(**kwargs)
        if not MAP_IMAGE_PATH.is_file():
            raise FileNotFoundError(f"REDLINE map artwork is missing: {MAP_IMAGE_PATH}")

        self.layout_data = layout
        self.direction = [0, 0]
        self.camera_x = 0.0
        self.camera_y = 0.0

        spawn = next(
            (item for item in layout.get("scenes", [])
             if item.get("spawn") == "survivor"),
            None,
        )
        if spawn:
            self.player_x = (
                (spawn["tile_x"] + spawn["tile_w"] / 2) / 128.0
            ) * WORLD_W
            self.player_y = WORLD_H - (
                (spawn["tile_y"] + spawn["tile_h"] / 2) / 100.0
            ) * WORLD_H
        else:
            self.player_x = WORLD_W * 0.82
            self.player_y = WORLD_H * 0.82

        # This is the exact supplied Redline Train Escape Map artwork, not a
        # regenerated tile diagram or a placeholder room layout.
        self.map_image = Image(
            source=str(MAP_IMAGE_PATH),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(None, None),
            size=(WORLD_W, WORLD_H),
            pos=self.pos,
        )
        self.add_widget(self.map_image)

        self.player_sprite = SurvivorSprite()
        self.add_widget(self.player_sprite)
        self.bind(pos=self._layout_world, size=self._layout_world)
        self._layout_world()
        self._clock = Clock.schedule_interval(self._update, 1 / 30)

    def set_direction(self, axis, value):
        self.direction[axis] = value

    def _update(self, dt):
        dx, dy = self.direction
        length = (dx * dx + dy * dy) ** 0.5
        if length:
            step = MOVE_SPEED * min(max(dt, 0.0), 0.05)
            self.player_x += (dx / length) * step
            self.player_y += (dy / length) * step
            self.player_x = max(12, min(WORLD_W - 12, self.player_x))
            self.player_y = max(12, min(WORLD_H - 12, self.player_y))
        self._layout_world()

    def _layout_world(self, *_):
        max_x = max(0.0, WORLD_W - self.width)
        max_y = max(0.0, WORLD_H - self.height)
        self.camera_x = max(0.0, min(max_x, self.player_x - self.width / 2))
        self.camera_y = max(0.0, min(max_y, self.player_y - self.height / 2))

        self.map_image.pos = (self.x - self.camera_x, self.y - self.camera_y)
        self.player_sprite.pos = (
            self.x + self.player_x - self.camera_x - self.player_sprite.width / 2,
            self.y + self.player_y - self.camera_y - self.player_sprite.height / 2,
        )

    def on_parent(self, *_):
        if self.parent is None and hasattr(self, "_clock"):
            self._clock.cancel()


class ExploreScreen(BoxLayout):
    """Free-roam mode over the supplied illustrated Train Escape map."""

    def __init__(self, on_back, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(5),
                         padding=dp(8), **kwargs)
        self.on_back = on_back
        layout = load_map_layout()

        header = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        title = Label(
            text="REDLINE  /  TRAIN ESCAPE",
            bold=True,
            halign="left",
            valign="middle",
        )
        title.bind(size=lambda widget, size: setattr(widget, "text_size", size))
        header.add_widget(title)
        back = Button(text="MENU", size_hint_x=None, width=dp(82))
        back.bind(on_release=lambda *_: self.on_back())
        header.add_widget(back)
        self.add_widget(header)

        self.world = ExploreWorld(layout, size_hint=(1, 1))
        self.add_widget(self.world)

        controls = BoxLayout(size_hint_y=None, height=dp(108), spacing=dp(6))
        controls.add_widget(Label(
            text="EXPLORE MAP 01",
            size_hint_x=0.65,
            bold=True,
            color=(0.82, 0.84, 0.86, 1),
        ))
        pad = BoxLayout(orientation="vertical", spacing=dp(3))
        middle = BoxLayout(spacing=dp(3))
        up, down, left, right = (Button(text=label) for label in ("▲", "▼", "◀", "▶"))
        middle.add_widget(left)
        middle.add_widget(up)
        middle.add_widget(right)
        pad.add_widget(middle)
        pad.add_widget(down)
        controls.add_widget(pad)
        self.add_widget(controls)

        # Hold-to-move touch controls. Releasing a control always stops it.
        up.bind(on_press=lambda *_: self.world.set_direction(1, 1),
                on_release=lambda *_: self.world.set_direction(1, 0))
        down.bind(on_press=lambda *_: self.world.set_direction(1, -1),
                  on_release=lambda *_: self.world.set_direction(1, 0))
        left.bind(on_press=lambda *_: self.world.set_direction(0, -1),
                  on_release=lambda *_: self.world.set_direction(0, 0))
        right.bind(on_press=lambda *_: self.world.set_direction(0, 1),
                   on_release=lambda *_: self.world.set_direction(0, 0))
