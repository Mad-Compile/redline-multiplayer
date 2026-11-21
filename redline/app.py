"""Kivy application bootstrap and stable screen navigation for REDLINE."""
from kivy.app import App
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition

from redline.menu import MainMenu


class RedlineApp(App):
    title = "REDLINE"

    def build(self):
        Window.clearcolor = (0.035, 0.047, 0.055, 1)
        try:
            Logger.info("REDLINE: starting Python/Kivy main menu")
            self.screen_manager = ScreenManager(transition=SlideTransition(duration=0.18))
            menu_screen = Screen(name="menu")
            menu_screen.add_widget(MainMenu())
            self.screen_manager.add_widget(menu_screen)
            Logger.info("REDLINE: main menu constructed successfully")
            return self.screen_manager
        except Exception as exc:
            Logger.exception("REDLINE: fatal exception while constructing the main menu")
            panel = BoxLayout(orientation="vertical", padding=24, spacing=16)
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

    def show_screen(self, name, widget=None):
        """Display a screen through ScreenManager; never replace App.root at runtime."""
        manager = getattr(self, "screen_manager", None)
        if manager is None:
            raise RuntimeError("REDLINE screen manager has not been initialized")

        if widget is not None:
            if manager.has_screen(name):
                manager.remove_widget(manager.get_screen(name))
            screen = Screen(name=name)
            screen.add_widget(widget)
            manager.add_widget(screen)

        if not manager.has_screen(name):
            raise ValueError(f"REDLINE screen is not registered: {name}")

        manager.current = name
        Logger.info("REDLINE: switched to screen '%s'" % name)
        return manager.get_screen(name)

    def on_pause(self):
        return True


if __name__ == "__main__":
    RedlineApp().run()
