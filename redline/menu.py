"""REDLINE menu built with the intact original button artwork.

The historical ZIP is preserved unchanged. It was truncated during upload:
the three button images are complete, but the background image and ZIP
directory are missing. A repaired ZIP contains only the three recovered
button files. The menu explicitly marks its temporary plain background.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image as PILImage
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider


ARTWORK = {
    "practice": "assets/menu/practice_button.webp",
    "match": "assets/menu/start_match_button.webp",
    "settings": "assets/menu/settings_button.webp",
}


class ArtworkButton(ButtonBehavior, Image):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.fit_mode = "fill"
        self._callback = callback
        self.bind(on_release=self._activate)

    def _activate(self, *_):
        self._callback()


class MainMenu(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._music = None
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

    def _build_menu(self):
        self._background_color = Color(0.035, 0.047, 0.055, 1)
        self._background_rect = Rectangle(pos=self.pos, size=self.size)
        self.canvas.before.add(self._background_color)
        self.canvas.before.add(self._background_rect)
        self.bind(pos=self._update_background, size=self._update_background)

        warning = Label(
            text="ORIGINAL MENU BACKGROUND ART NEEDS RESTORATION",
            color=(1.0, 0.55, 0.35, 1),
            font_size="14sp",
            size_hint=(1, 0.055),
            pos_hint={"x": 0, "top": 0.99},
        )
        self.add_widget(warning)

        # Coordinates preserve the supplied 1600x900 button composition.
        self.add_widget(ArtworkButton(
            self._open_practice,
            source=self._art_paths["practice"],
            size_hint=(0.328, 0.174),
            pos_hint={"x": 0.603, "top": 0.828},
        ))
        self.add_widget(ArtworkButton(
            self._open_match,
            source=self._art_paths["match"],
            size_hint=(0.328, 0.116),
            pos_hint={"x": 0.603, "top": 0.594},
        ))
        self.add_widget(ArtworkButton(
            self._open_settings,
            source=self._art_paths["settings"],
            size_hint=(0.328, 0.180),
            pos_hint={"x": 0.603, "top": 0.383},
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
        content = BoxLayout(orientation="vertical", spacing=16, padding=20)
        content.add_widget(Label(text="MASTER VOLUME", size_hint_y=None, height=32))
        current_volume = self._music.volume if self._music else 0.65
        slider = Slider(min=0.0, max=1.0, value=current_volume)
        content.add_widget(slider)
        close = Button(text="BACK", size_hint_y=None, height=48)
        content.add_widget(close)
        popup = Popup(title="FIELD SETTINGS", content=content, size_hint=(0.72, 0.40))
        def set_volume(_slider, value):
            if self._music:
                self._music.volume = value
        slider.bind(value=set_volume)
        close.bind(on_release=popup.dismiss)
        popup.open()
