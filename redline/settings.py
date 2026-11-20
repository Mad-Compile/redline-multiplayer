"""REDLINE native settings screen: illustrated controls and persistent preferences."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from kivy.app import App
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from redline.menu import ArtworkButton


DEFAULT_PREFERENCES = {
    "master_volume": 1.0,
    "music_volume": 0.65,
    "sfx_volume": 0.52,
    "resolution": "100%",
    "shadows": "High",
    "player_names": "On",
    "control_stick": "Dynamic",
    "control_device": "Touch",
}

SELECT_OPTIONS = {
    "resolution": ["75%", "85%", "100%"],
    "shadows": ["Off", "Low", "High"],
    "player_names": ["On", "Off"],
    "control_stick": ["Dynamic", "Fixed"],
    "control_device": ["Touch", "Controller"],
}

SELECT_LABELS = {
    "resolution": "RESOLUTION",
    "shadows": "SHADOWS",
    "player_names": "PLAYER NAMES",
    "control_stick": "CONTROL STICK",
    "control_device": "CONTROL DEVICE",
}

VOLUME_LABELS = {
    "master_volume": "MASTER VOLUME",
    "music_volume": "MUSIC VOLUME",
    "sfx_volume": "SFX VOLUME",
}


def load_preferences(path: Path) -> dict:
    values = dict(DEFAULT_PREFERENCES)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            for key in values:
                if key in loaded:
                    values[key] = loaded[key]
    except (OSError, ValueError, TypeError):
        pass

    for key in VOLUME_LABELS:
        try:
            values[key] = min(1.0, max(0.0, float(values[key])))
        except (TypeError, ValueError):
            values[key] = DEFAULT_PREFERENCES[key]

    for key, options in SELECT_OPTIONS.items():
        if values[key] not in options:
            values[key] = DEFAULT_PREFERENCES[key]
    return values


def save_preferences(path: Path, values: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(values, indent=2), encoding="utf-8")
    temporary.replace(path)


class OutlinedText(FloatLayout):
    """Bold game-style text with a dark printed edge, built from native labels."""

    def __init__(self, text="", font_size=18, align="center", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_size
        self.align = align
        self._layers = []
        for dx, dy in (
            (-1, -1), (0, -1), (1, -1), (-1, 0),
            (1, 0), (-1, 1), (0, 1), (1, 1),
        ):
            layer = Label(
                text=text,
                font_name="Roboto",
                bold=True,
                font_size=sp(font_size),
                color=(0.008, 0.010, 0.014, 1),
                halign=align,
                valign="middle",
            )
            self.add_widget(layer)
            self._layers.append((layer, dx, dy))

        self._face = Label(
            text=text,
            font_name="Roboto",
            bold=True,
            font_size=sp(font_size),
            color=(0.94, 0.95, 0.96, 1),
            halign=align,
            valign="middle",
        )
        self.add_widget(self._face)
        self.bind(pos=self._layout_layers, size=self._layout_layers)
        self._layout_layers()

    def set_text(self, text):
        self.text = text
        for layer, _, _ in self._layers:
            layer.text = text
        self._face.text = text

    def _layout_layers(self, *_):
        for layer, dx, dy in self._layers:
            layer.pos = (self.x + dp(dx), self.y + dp(dy))
            layer.size = self.size
            layer.text_size = self.size
        self._face.pos = self.pos
        self._face.size = self.size
        self._face.text_size = self.size


class GradientBackdrop(FloatLayout):
    """Charcoal-to-black industrial backdrop drawn with native Kivy strips."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._strips = []
        with self.canvas.before:
            for index in range(72):
                ratio = index / 71.0
                top = (0.105, 0.115, 0.13)
                bottom = (0.018, 0.022, 0.028)
                color = tuple(top[c] * (1.0 - ratio) + bottom[c] * ratio for c in range(3))
                Color(*color, 1)
                rect = Rectangle()
                self._strips.append(rect)
        self.bind(pos=self._layout_strips, size=self._layout_strips)
        self._layout_strips()

    def _layout_strips(self, *_):
        if not self.height:
            return
        strip_height = self.height / len(self._strips) + 1
        for index, rect in enumerate(self._strips):
            rect.pos = (self.x, self.y + index * self.height / len(self._strips))
            rect.size = (self.width, strip_height)


class HeaderStrip(FloatLayout):
    """Strong blue title strip with an inset lower edge."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.035, 0.040, 0.048, 1)
            self._bar = Rectangle(pos=self.pos, size=self.size)
            Color(0.82, 0.075, 0.085, 1)
            self._highlight = Rectangle()
            Color(0.012, 0.014, 0.018, 1)
            self._edge = Rectangle()
        self.bind(pos=self._layout, size=self._layout)
        self._layout()

    def _layout(self, *_):
        self._bar.pos, self._bar.size = self.pos, self.size
        self._highlight.pos = (self.x, self.y + self.height - dp(3))
        self._highlight.size = (self.width, dp(3))
        self._edge.pos = (self.x, self.y)
        self._edge.size = (self.width, dp(3))


class RedlineSettingsPanel(BoxLayout):
    """Dark steel panel with restrained red edging and a soft lower shadow."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.0, 0.0, 0.0, 0.52)
            self._shadow = RoundedRectangle(radius=[dp(8)])
            Color(0.075, 0.082, 0.092, 1)
            self._panel = RoundedRectangle(radius=[dp(8)])
            Color(0.82, 0.075, 0.085, 0.82)
            self._rim = Line(rounded_rectangle=(0, 0, 1, 1, dp(8)), width=1.05)
            Color(0.28, 0.30, 0.33, 0.8)
            self._inner = Line(rounded_rectangle=(0, 0, 1, 1, dp(6)), width=0.7)
        self.bind(pos=self._layout_panel, size=self._layout_panel)
        self._layout_panel()

    def _layout_panel(self, *_):
        x, y = self.pos
        w, h = self.size
        self._shadow.pos = (x + dp(2), y - dp(3))
        self._shadow.size = (w, h)
        self._panel.pos = self.pos
        self._panel.size = self.size
        self._rim.rounded_rectangle = (x, y, w, h, dp(8))
        self._inner.rounded_rectangle = (x + dp(3), y + dp(3), max(0, w - dp(6)), max(0, h - dp(6)), dp(6))


class RedlineValueDisplay(FloatLayout):
    """Black inset value window, matching the supplied settings reference."""

    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.012, 0.018, 0.027, 1)
            self._rect = RoundedRectangle(radius=[dp(3)])
            Color(0.02, 0.03, 0.05, 0.8)
            self._line = Line(rounded_rectangle=(0, 0, 1, 1, dp(3)), width=0.8)
        self.label = OutlinedText(text=text, font_size=17)
        self.add_widget(self.label)
        self.bind(pos=self._layout, size=self._layout)
        self._layout()

    def set_text(self, value):
        self.label.set_text(value)

    def _layout(self, *_):
        self._rect.pos, self._rect.size = self.pos, self.size
        self._line.rounded_rectangle = (*self.pos, *self.size, dp(3))
        self.label.pos, self.label.size = self.pos, self.size


class VolumeSlider(FloatLayout):
    """Custom draggable yellow/orange volume slider."""

    def __init__(self, value=1.0, on_change=None, **kwargs):
        super().__init__(**kwargs)
        self.value = min(1.0, max(0.0, float(value)))
        self.on_change = on_change
        with self.canvas:
            Color(0.02, 0.025, 0.035, 1)
            self._track = RoundedRectangle(radius=[dp(5)])
            Color(0.78, 0.055, 0.065, 1)
            self._fill = RoundedRectangle(radius=[dp(5)])
            Color(0.98, 0.22, 0.20, 1)
            self._knob = RoundedRectangle(radius=[dp(4)])
            Color(0.20, 0.025, 0.03, 1)
            self._knob_edge = Line(rounded_rectangle=(0, 0, 1, 1, dp(4)), width=1.3)
            Color(1.0, 0.72, 0.70, 0.88)
            self._shine = Line(points=[0, 0, 0, 0], width=1.0)
        self.bind(pos=self._layout_slider, size=self._layout_slider)
        self._layout_slider()

    def _layout_slider(self, *_):
        pad = dp(20)
        track_x = self.x + pad
        track_y = self.center_y - dp(5)
        track_w = max(dp(30), self.width - 2 * pad)
        self._track.pos = (track_x, track_y)
        self._track.size = (track_w, dp(10))
        self._fill.pos = (track_x, track_y)
        self._fill.size = (track_w * self.value, dp(10))
        knob_w, knob_h = dp(22), dp(24)
        knob_x = track_x + track_w * self.value - knob_w / 2
        self._knob.pos = (knob_x, self.center_y - knob_h / 2)
        self._knob.size = (knob_w, knob_h)
        self._knob_edge.rounded_rectangle = (knob_x, self.center_y - knob_h / 2, knob_w, knob_h, dp(4))
        self._shine.points = (knob_x + dp(5), self.center_y + dp(6), knob_x + knob_w - dp(5), self.center_y + dp(6))

    def _set_from_touch(self, touch):
        pad = dp(20)
        usable = max(dp(1), self.width - 2 * pad)
        value = min(1.0, max(0.0, (touch.x - self.x - pad) / usable))
        if abs(value - self.value) >= 0.002:
            self.value = value
            self._layout_slider()
            if self.on_change:
                self.on_change(value)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._set_from_touch(touch)
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self._set_from_touch(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self._set_from_touch(touch)
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


class RedlineVolumePanel(RedlineSettingsPanel):
    def __init__(self, key, value, on_change, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(2), padding=(dp(14), dp(7)), **kwargs)
        title = OutlinedText(text=VOLUME_LABELS[key], font_size=15, size_hint_y=None, height=dp(26))
        self.add_widget(title)
        slider = VolumeSlider(value=value, on_change=on_change, size_hint_y=None, height=dp(34))
        self.add_widget(slider)
        self.slider = slider


class RedlineSelectorPanel(RedlineSettingsPanel):
    def __init__(self, key, value, options, on_step, left_image, right_image, click_sound, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(5), padding=(dp(12), dp(5)), **kwargs)
        self.key = key
        self.options = options
        self.on_step = on_step

        title = OutlinedText(
            text=SELECT_LABELS[key],
            font_size=15,
            align="left",
            size_hint_x=0.43,
        )
        self.add_widget(title)

        controls = BoxLayout(orientation="horizontal", spacing=dp(3), size_hint_x=0.57)
        self.add_widget(controls)

        self.left_button = ArtworkButton(
            lambda: self.on_step(self.key, -1),
            click_sound=click_sound,
            source=left_image,
            size_hint=(None, None),
            size=(dp(54), dp(54)),
        )
        controls.add_widget(self.left_button)

        self.value_display = RedlineValueDisplay(text=value)
        controls.add_widget(self.value_display)

        self.right_button = ArtworkButton(
            lambda: self.on_step(self.key, 1),
            click_sound=click_sound,
            source=right_image,
            size_hint=(None, None),
            size=(dp(54), dp(54)),
        )
        controls.add_widget(self.right_button)

    def set_value(self, value):
        self.value_display.set_text(value)


class SettingsScreen(FloatLayout):
    """Landscape settings screen built entirely with native Kivy widgets/canvas."""

    def __init__(
        self,
        on_back: Callable[[], None],
        click_sound=None,
        audio_callback: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self._on_back = on_back
        self._click_sound = click_sound
        self._audio_callback = audio_callback
        self._project_root = Path(__file__).resolve().parents[1]
        self._settings_path = Path(app.user_data_dir) / "redline_settings.json"
        self.preferences = load_preferences(self._settings_path)
        self._ui_paths = self._prepare_button_images()
        self._build_screen()

    def _prepare_button_images(self):
        source_dir = self._project_root / "assets" / "ui" / "settings"
        output_dir = Path(App.get_running_app().user_data_dir) / "settings_ui"
        output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "back": "back_button.webp",
            "left": "arrow_left.webp",
            "right": "arrow_right.webp",
        }
        paths = {}
        for key, filename in mapping.items():
            source = source_dir / filename
            if not source.is_file():
                raise FileNotFoundError(f"REDLINE settings UI artwork missing: {source}")
            output = output_dir / f"{key}.png"
            # Regenerate rather than trusting filesystem mtimes. Android app
            # updates can preserve user_data_dir with stale, invalid image caches.
            from PIL import Image as PILImage
            with PILImage.open(source) as image:
                image.load()
                image.convert("RGBA").save(output, format="PNG")
            paths[key] = str(output)
        return paths

    def _build_screen(self):
        self._backdrop = GradientBackdrop(size_hint=(1, 1))
        self.add_widget(self._backdrop)

        self._header = HeaderStrip(size_hint=(1, 0.125), pos_hint={"x": 0, "top": 1})
        self.add_widget(self._header)

        self._back_button = ArtworkButton(
            self._go_back,
            click_sound=self._click_sound,
            source=self._ui_paths["back"],
            size_hint=(None, None),
            size=(dp(66), dp(66)),
            pos_hint={"x": 0.006, "top": 0.99},
        )
        self.add_widget(self._back_button)

        title = OutlinedText(
            text="SETTINGS",
            font_size=29,
            size_hint=(0.40, 0.105),
            pos_hint={"center_x": 0.5, "top": 0.985},
        )
        self.add_widget(title)

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=(dp(6), dp(8)),
            size_hint_x=1,
        )
        content.bind(minimum_height=content.setter("height"))

        for key in ("master_volume", "music_volume", "sfx_volume"):
            panel = RedlineVolumePanel(
                key,
                self.preferences[key],
                lambda value, setting=key: self._set_volume(setting, value),
                size_hint_y=None,
                height=dp(78),
            )
            content.add_widget(panel)

        self._selectors = {}
        for key, options in SELECT_OPTIONS.items():
            panel = RedlineSelectorPanel(
                key=key,
                value=self.preferences[key],
                options=options,
                on_step=self._step_setting,
                left_image=self._ui_paths["left"],
                right_image=self._ui_paths["right"],
                click_sound=self._click_sound,
                size_hint_y=None,
                height=dp(70),
            )
            content.add_widget(panel)
            self._selectors[key] = panel

        self._scroll = ScrollView(
            size_hint=(0.50, 0.84),
            pos_hint={"center_x": 0.5, "top": 0.865},
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(5),
            scroll_type=["bars", "content"],
            bar_color=(0.85, 0.94, 1, 0.85),
            bar_inactive_color=(0.1, 0.2, 0.3, 0.35),
        )
        content.size_hint_y = None
        self._scroll.add_widget(content)
        self.add_widget(self._scroll)

    def _persist(self):
        save_preferences(self._settings_path, self.preferences)

    def _set_volume(self, key, value):
        self.preferences[key] = min(1.0, max(0.0, float(value)))
        self._persist()
        if self._audio_callback:
            self._audio_callback()

    def _step_setting(self, key, step):
        options = SELECT_OPTIONS[key]
        current = options.index(self.preferences[key])
        selected = options[(current + step) % len(options)]
        self.preferences[key] = selected
        self._selectors[key].set_value(selected)
        self._persist()

    def _go_back(self):
        self._persist()
        self._on_back()
