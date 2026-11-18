"""Kivy application bootstrap for REDLINE."""
from kivy.app import App
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from redline.menu import MainMenu


class RedlineApp(App):
    title = "REDLINE"

    def build(self):
        Window.clearcolor = (0.035, 0.047, 0.055, 1)
        try:
            Logger.info("REDLINE: starting Python/Kivy main menu")
            menu = MainMenu()
            Logger.info("REDLINE: main menu constructed successfully")
            return menu
        except Exception as exc:
            # Keep the process alive and show the exact startup failure instead
            # of silently disappearing immediately after the Android splash.
            Logger.exception("REDLINE: fatal exception while constructing the main menu")
            panel = BoxLayout(
                orientation="vertical",
                padding=24,
                spacing=16,
            )
            panel.add_widget(Label(
                text="REDLINE COULD NOT START",
                font_size="24sp",
                bold=True,
                size_hint_y=0.25,
            ))
            panel.add_widget(Label(
                text=f"{type(exc).__name__}: {exc}",
                font_size="16sp",
                halign="left",
                valign="middle",
            ))
            return panel

    def on_pause(self):
        return True


if __name__ == "__main__":
    RedlineApp().run()
