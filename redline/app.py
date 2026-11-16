"""Kivy application bootstrap for REDLINE."""
from kivy.app import App
from kivy.core.window import Window

from redline.menu import MainMenu


class RedlineApp(App):
    title = "REDLINE"

    def build(self):
        Window.clearcolor = (0.035, 0.047, 0.055, 1)
        return MainMenu()

    def on_pause(self):
        return True


if __name__ == "__main__":
    RedlineApp().run()
