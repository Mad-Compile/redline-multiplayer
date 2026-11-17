"""REDLINE main menu using the recovered original button artwork.

The original menu background is intentionally not recreated here. A neutral
dark canvas remains until the production background artwork is supplied.
"""
from __future__ import annotations

import math
import struct
import wave
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from kivy.animation import Animation
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.graphics import PopMatrix, PushMatrix, Rectangle, Scale
from kivy.graphics import Color
from kivy.properties import NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup


ARTWORK = {
    "practice": "assets/menu/practice_button.webp",
    "match": "assets/menu/start_match_button.webp",
    "settings": "assets/menu/settings_button.webp",
}


class ArtworkButton(ButtonBehavior, Image):
    """Original image button with one tactile press/release animation."""

    press_scale = NumericProperty(1.0)

    def __init__(self, callback, click_sound=None, **kwargs):
        super().__init__(**kwargs)
        self.fit_mode = "fill"
        self._callback = callback
        self._click_sound = click_sound

        with self.canvas.before:
            PushMatrix()
            self._press_transform = Scale(
                x=1.0, y=1.0, z=1.0,
                origin=(self.center_x, self.center_y, 0),
            )
        with self.canvas.after:
            PopMatrix()

        self.bind(pos=self._sync_transform, size=self._sync_transform)
        self.bind(press_scale=self._apply_press_scale)
        self.bind(on_press=self._on_pressed, on_release=self._on_released)

    def _sync_transform(self, *_):
        self._press_transform.origin = (self.center_x, self.center_y, 0)

    def _apply_press_scale(self, _instance, value):
        self._press_transform.x = value
        self._press_transform.y = value

    def _on_pressed(self, *_):
        Animation.cancel_all(self, "press_scale")
        Animation(
            press_scale=0.94,
            duration=0.055,
            t="out_quad",
        ).start(self)

    def _on_released(self, *_):
        Animation.cancel_all(self, "press_scale")
        Animation(
            press_scale=1.0,
            duration=0.12,
            t="out_back",
        ).start(self)

        if self._click_sound:
            self._click_sound.stop()
            self._click_sound.play()
        self._callback()


class MainMenu(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._music = None
        self._click_sound = self._prepare_click_sound()
        self._art_paths = self._prepare_artwork()
        self._build_menu()
        self._start_optional_music()

    def _prepare_artwork(self):
        project_root = Path(__file__).resolve().parents[1]
        archive_path = project_root / "assets" / "menu" / "menu_buttons_recovered.zip"
        if not archive_path.is_file():
            raise FileNotFoundError(
                "Recovered original REDLINE menu buttons are missing: " + str(archive_path)
            )

        output_dir = Path(App.get_running_app().user_data_dir) / "menu_art"
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = {}
        with ZipFile(archive_path, "r") as archive:
            for key, member in ARTWORK.items():
                raw = archive.read(member)
                output_path = output_dir / (key + ".png")
                with PILImage.open(BytesIO(raw)) as source:
                    source.convert("RGBA").save(output_path, format="PNG")
                paths[key] = str(output_path)
        return paths

    def _prepare_click_sound(self):
        """Create a tiny one-shot UI click locally; replaceable by supplied SFX."""
        output_dir = Path(App.get_running_app().user_data_dir) / "ui_audio"
        output_dir.mkdir(parents=True, exist_ok=True)
        sound_path = output_dir / "button_click.wav"

        if not sound_path.is_file():
            sample_rate = 22050
            duration = 0.060
            frame_count = int(sample_rate * duration)
            samples = bytearray()

            for index in range(frame_count):
                time_s = index / sample_rate
                attack = 1.0 - math.exp(-time_s / 0.00025)
                decay = math.exp(-time_s / 0.009)
                frequency = 2450.0 - (650.0 * time_s / duration)
                click = (
                    0.62 * math.sin(2.0 * math.pi * frequency * time_s)
                    + 0.24 * math.sin(2.0 * math.pi * 3900.0 * time_s)
                    + 0.10 * math.sin(2.0 * math.pi * 720.0 * time_s)
                )
                value = max(-1.0, min(1.0, click * attack * decay * 0.68))
                samples.extend(struct.pack("<h", int(value * 32767)))

            with wave.open(str(sound_path), "wb") as sound_file:
                sound_file.setnchannels(1)
                sound_file.setsampwidth(2)
                sound_file.setframerate(sample_rate)
                sound_file.writeframes(bytes(samples))

        sound = SoundLoader.load(str(sound_path))
        if sound:
            sound.loop = False
            sound.volume = 0.52
        return sound

    def _build_menu(self):
        # Keep the background deliberately neutral until the user's art arrives.
        self._background_color = Color(0.035, 0.047, 0.055, 1)
        self._background_rect = Rectangle(pos=self.pos, size=self.size)
        self.canvas.before.add(self._background_color)
        self.canvas.before.add(self._background_rect)
        self.bind(pos=self._update_background, size=self._update_background)

        # Original supplied buttons, moved to the LEFT side of the screen.
        # Their only motion is the short scale-down / scale-up click response.
        self.add_widget(ArtworkButton(
            self._open_practice,
            click_sound=self._click_sound,
            source=self._art_paths["practice"],
            size_hint=(0.328, 0.174),
            pos_hint={"x": 0.055, "top": 0.828},
        ))
        self.add_widget(ArtworkButton(
            self._open_match,
            click_sound=self._click_sound,
            source=self._art_paths["match"],
            size_hint=(0.328, 0.116),
            pos_hint={"x": 0.055, "top": 0.594},
        ))
        self.add_widget(ArtworkButton(
            self._open_settings,
            click_sound=self._click_sound,
            source=self._art_paths["settings"],
            size_hint=(0.328, 0.180),
            pos_hint={"x": 0.055, "top": 0.383},
        ))

    def _update_background(self, *_):
        self._background_rect.pos = self.pos
        self._background_rect.size = self.size

    def _start_optional_music(self):
        project_root = Path(__file__).resolve().parents[1]
        candidates = [
            project_root / "assets" / "audio" / "Redline Theme Song.mp3",
            project_root / "assets" / "audio" / "redline_theme.mp3",
        ]
        for candidate in candidates:
            if candidate.is_file():
                self._music = SoundLoader.load(str(candidate))
                if self._music:
                    self._music.loop = True
                    self._music.volume = 0.65
                    self._music.play()
                break

    def _popup(self, title, message):
        content = BoxLayout(orientation="vertical", spacing=16, padding=20)
        label = Label(text=message, halign="center", valign="middle")
        label.bind(size=lambda instance, size: setattr(instance, "text_size", size))
        content.add_widget(label)
        close = Button(text="BACK", size_hint_y=None, height=48)
        content.add_widget(close)
        popup = Popup(title=title, content=content, size_hint=(0.78, 0.48))
        close.bind(on_release=popup.dismiss)
        popup.open()

    def _open_practice(self):
        # MAP 01 is integrated as a source-driven, interactive location browser.
        # It is explicitly a schematic preview, not a false playable-match claim.
        app = App.get_running_app()
        from redline.gameplay.map_screen import MapScreen

        app.root = MapScreen(on_back=lambda: setattr(app, "root", self))

    def _open_match(self):
        self._popup(
            "MULTIPLAYER",
            "The multiplayer session and authoritative server are not "
            "implemented yet. No fake lobby or simulated match is shown.",
        )

    def _open_settings(self):
        # No generic Kivy volume panel: the Settings screen is intentionally
        # held until the REDLINE-specific panel/control artwork is supplied.
        return
