"""REDLINE menu using the original supplied menu artwork archive.

The archive is preserved unchanged. Its four WebP files are decoded to PNG in
Kivy's writable app-data directory because Android asset paths are read-only.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image as PILImage
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout


ARTWORK = {
    "background": "assets/menu/menu_background.webp",
    "practice": "assets/menu/practice_button.webp",
    "match": "assets/menu/start_match_button.webp",
    "settings": "assets/menu/settings_button.webp",
}


class ArtworkButton(ButtonBehavior, Image):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.fit_mode = "fill"
        self.allow_stretch = True
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
        archive_path = project_root / "assets" / "menu" / "menu_art.zip"
        if not archive_path.is_file():
            raise FileNotFoundError(
                "Supplied REDLINE menu archive is missing: " + str(archive_path)
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
        background = Image(
            source=self._art_paths["background"],
            fit_mode="fill",
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        self.add_widget(background)

        # Coordinates preserve the supplied 1600x900 menu composition.
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
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.78, 0.48),
            auto_dismiss=True,
        )
        close.bind(on_release=popup.dismiss)
        popup.open()

    def _open_practice(self):
        self._popup(
            "PRACTICE MODE",
            "The Python gameplay scene is not connected yet. "
            "This button will launch the real practice match once its map, "
            "character assets and controls are integrated.",
        )

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
        popup = Popup(
            title="FIELD SETTINGS",
            content=content,
            size_hint=(0.72, 0.40),
            auto_dismiss=True,
        )
        def set_volume(_slider, value):
            if self._music:
                self._music.volume = value
        slider.bind(value=set_volume)
        close.bind(on_release=popup.dismiss)
        popup.open()
