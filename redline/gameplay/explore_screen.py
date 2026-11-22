"""Mobile first-person exploration screen for REDLINE MAP 01."""
from __future__ import annotations
import math
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from redline.gameplay.map_data import load_map_layout
from redline.gameplay.raycast_world import FOV, build_world, cast_ray, current_location, move_player

class FirstPersonView(Widget):
    """Column raycaster with touch joystick, swipe-look and animated head bob."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.world = build_world(load_map_layout())
        self.player_x, self.player_y = self.world["spawn"]
        self.angle = math.radians(-90)
        self.move_x = self.move_y = 0.0
        self.sprinting = False
        self._touch_roles = {}
        self._location_label = None
        self._bob = self._elapsed = 0.0
        self._clock = Clock.schedule_interval(self.update, 1 / 20)
        self.bind(pos=self.draw_scene, size=self.draw_scene)
        self.draw_scene()

    def attach_location_label(self, label):
        self._location_label = label

    def set_sprint(self, active):
        self.sprinting = bool(active)

    def interact(self):
        if self._location_label:
            self._location_label.text = current_location(self.world, self.player_x, self.player_y)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        role = "move" if touch.x < self.center_x else "look"
        self._touch_roles[touch.uid] = role
        if role == "move":
            self._update_joystick(touch.x, touch.y)
        else:
            touch.ud["redline_last_x"] = touch.x
        return True

    def on_touch_move(self, touch):
        role = self._touch_roles.get(touch.uid)
        if role == "move":
            self._update_joystick(touch.x, touch.y)
            return True
        if role == "look":
            last = touch.ud.get("redline_last_x", touch.x)
            self.angle += (touch.x - last) * 0.006
            touch.ud["redline_last_x"] = touch.x
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        role = self._touch_roles.pop(touch.uid, None)
        if role == "move":
            self.move_x = self.move_y = 0.0
            return True
        if role == "look":
            return True
        return super().on_touch_up(touch)

    def _update_joystick(self, x, y):
        dx = (x - self.x - self.width * 0.25) / max(1, self.width * 0.19)
        dy = (y - self.y - self.height * 0.30) / max(1, self.height * 0.24)
        length = math.hypot(dx, dy)
        if length > 1:
            dx, dy = dx / length, dy / length
        self.move_x, self.move_y = dx, dy

    def update(self, dt):
        dt = min(max(dt, 0), 0.06)
        speed = 3.2 if self.sprinting else 2.0
        fx, fy = math.cos(self.angle), math.sin(self.angle)
        rx, ry = -fy, fx
        dx = (fx * self.move_y + rx * self.move_x) * speed * dt
        dy = (fy * self.move_y + ry * self.move_x) * speed * dt
        if dx or dy:
            self.player_x, self.player_y = move_player(
                self.world, self.player_x, self.player_y, dx, dy
            )
            self._elapsed += dt * (2.7 if self.sprinting else 1.8)
            self._bob = math.sin(self._elapsed * 2) * dp(5 if self.sprinting else 3)
        else:
            self._bob *= 0.82
        self.draw_scene()

    def draw_scene(self, *_):
        if self.width < 2 or self.height < 2:
            return
        self.canvas.clear()
        w, h = self.width, self.height
        columns = max(72, min(112, int(w / dp(5))))
        col_w = w / columns
        horizon = self.y + h * 0.53 + self._bob * 0.18
        with self.canvas:
            Color(0.055, 0.063, 0.071, 1)
            Rectangle(pos=(self.x, horizon), size=(w, self.top - horizon))
            Color(0.16, 0.145, 0.13, 1)
            Rectangle(pos=(self.x, self.y), size=(w, horizon - self.y))
            for i in range(columns):
                camera = 2.0 * i / columns - 1.0
                ray_angle = self.angle + math.atan(camera * math.tan(FOV / 2))
                distance, side = cast_ray(self.world, self.player_x, self.player_y, ray_angle)
                distance *= math.cos(ray_angle - self.angle)
                wall_h = min(h * 1.65, h * 0.82 / max(0.12, distance))
                shade = max(0.16, 0.82 - distance * 0.035) * (0.72 if side else 1)
                Color(0.38 * shade, 0.30 * shade, 0.27 * shade, 1)
                Rectangle(pos=(self.x + i * col_w, horizon - wall_h / 2),
                          size=(col_w + 1, wall_h))
            # Animated first-person sleeves provide visible run/step motion.
            bob = self._bob
            Color(0.12, 0.13, 0.14, 1)
            RoundedRectangle(pos=(self.center_x-dp(78), self.y-dp(16)+bob),
                             size=(dp(55), dp(90)), radius=[dp(18)])
            RoundedRectangle(pos=(self.center_x+dp(23), self.y-dp(16)+bob),
                             size=(dp(55), dp(90)), radius=[dp(18)])
            Color(0.48, 0.12, 0.10, 1)
            RoundedRectangle(pos=(self.center_x-dp(70), self.y+dp(28)+bob),
                             size=(dp(40), dp(42)), radius=[dp(10)])
            RoundedRectangle(pos=(self.center_x+dp(30), self.y+dp(28)+bob),
                             size=(dp(40), dp(42)), radius=[dp(10)])

class ExploreScreen(BoxLayout):
    """First-person free roam across all source-authored MAP 01 locations."""
    def __init__(self, on_back, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(4), padding=dp(6), **kwargs)
        self.on_back = on_back
        header = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.location_label = Label(text="SAFE HAVEN", bold=True,
            color=(0.92,0.92,0.92,1), halign="left", valign="middle")
        self.location_label.bind(size=lambda obj, value: setattr(obj,"text_size",value))
        header.add_widget(self.location_label)
        interact = Button(text="INTERACT", size_hint_x=None, width=dp(100))
        interact.bind(on_release=lambda *_: self.world.interact())
        header.add_widget(interact)
        back = Button(text="MENU", size_hint_x=None, width=dp(72))
        back.bind(on_release=lambda *_: self.on_back())
        header.add_widget(back)
        self.add_widget(header)
        self.world = FirstPersonView()
        self.world.attach_location_label(self.location_label)
        self.add_widget(self.world)
        footer = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        footer.add_widget(Label(text="LEFT: MOVE / STRAFE     RIGHT: SWIPE TO LOOK",
                                color=(0.68,0.70,0.72,1), font_size="11sp"))
        sprint = Button(text="HOLD TO SPRINT", size_hint_x=None, width=dp(145))
        sprint.bind(on_press=lambda *_: self.world.set_sprint(True),
                    on_release=lambda *_: self.world.set_sprint(False))
        footer.add_widget(sprint)
        self.add_widget(footer)

    def on_parent(self, *_):
        if self.parent is None and hasattr(self, "world"):
            self.world._clock.cancel()
