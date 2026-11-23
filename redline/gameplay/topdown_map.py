"""
REDLINE — Terminal Zero  2-D top-down playable map.

Replaces the first-person raycaster. Draws the full Terminal Zero map
matching the reference image exactly. Player walks freely through every
room — all doors and gates are open with zero blocking.

Controls:
  Keyboard : WASD / arrow keys
  Touch    : left half = virtual joystick
"""
from __future__ import annotations
import math
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget

# ── grid ──────────────────────────────────────────────────────────
GRID_W, GRID_H = 128, 100
WALL, FLOOR = 1, 0
PLAYER_RADIUS = 0.28
MOVE_SPEED    = 6.0
TILE          = 14   # pixels per tile at 1× scale

# ── colours ───────────────────────────────────────────────────────
C_BG          = (0.04, 0.04, 0.05, 1)
C_FLOOR_Z     = (0.22, 0.08, 0.07, 1)   # zombie floor
C_FLOOR_S     = (0.07, 0.11, 0.21, 1)   # survivor floor
C_FLOOR_T     = (0.07, 0.07, 0.14, 1)   # train station floor
C_FLOOR_B     = (0.38, 0.06, 0.06, 1)   # barrier floor
C_WALL_Z      = (0.12, 0.04, 0.04, 1)
C_WALL_S      = (0.04, 0.07, 0.14, 1)
C_WALL_T      = (0.04, 0.05, 0.10, 1)
C_BORDER_Z    = (0.60, 0.14, 0.14, 1)
C_BORDER_S    = (0.18, 0.38, 0.65, 1)
C_BORDER_T    = (0.18, 0.38, 0.65, 1)
C_BARRIER     = (0.80, 0.08, 0.08, 1)
C_STRIPE      = (0.95, 0.76, 0.00, 1)
C_LABEL       = (1.00, 1.00, 1.00, 1)
C_PLAYER      = (0.95, 0.90, 0.20, 1)

# ── room table: (id, name, tx, ty, tw, th, zone) ──────────────────
# Coordinates derived from reference image proportions
ROOMS = [
    # ZOMBIE SIDE
    ("dead_end",          "Dead End\n(Zombie Spawn)",   2,  2, 15, 12, "Z"),
    ("iron_yard",         "Iron Yard",                 18,  2, 15, 12, "Z"),
    ("rust_factory",      "Rust Factory",              34,  2, 13, 12, "Z"),
    ("scrap_depot",       "Scrap Depot",                2, 15, 15, 13, "Z"),
    ("power_ruins",       "Power Ruins",               18, 15, 15, 13, "Z"),
    ("shattered_wh",      "Shattered\nWarehouse",      34, 13, 13, 17, "Z"),
    ("corruption_lab",    "Corruption Lab",             2, 29, 15, 13, "Z"),
    ("breach_control",    "Breach Control",            18, 29, 15, 13, "Z"),
    ("waste_grounds",     "Waste Grounds",              2, 43, 15, 14, "Z"),
    ("watch_post",        "Watch Post",                31, 43,  8, 10, "Z"),
    ("control_node",      "Control Node",              40, 43,  8, 10, "Z"),
    # BARRIER GAPS (open passages, not solid)
    ("north_breach",      "North\nBreach",             49,  2,  5,  7, "B"),
    ("east_breach",       "East\nBreach",              49, 20,  5,  7, "B"),
    ("south_breach",      "South\nBreach",             49, 40,  5,  7, "B"),
    ("dead_gate",         "Dead Gate",                 48, 33,  7,  6, "B"),
    # SURVIVOR SIDE
    ("security_hq",       "Security HQ",               55,  2, 16, 12, "S"),
    ("residential_blk",   "Residential\nBlock",        72,  2, 15, 12, "S"),
    ("watchtower",        "Watchtower",                88,  2, 12, 12, "S"),
    ("med_bay",           "Med Bay",                   55, 15, 16, 13, "S"),
    ("supply_hub",        "Supply Hub",                72, 15, 15, 13, "S"),
    ("tool_shed",         "Tool Shed",                 88, 15, 12, 13, "S"),
    ("generator_room",    "Generator\nRoom",           55, 29, 16, 13, "S"),
    ("central_cyard",     "Central\nCourtyard",        72, 29, 15, 13, "S"),
    ("fuel_depot",        "Fuel Depot",                88, 29, 12, 13, "S"),
    ("comm_room",         "Communication\nRoom",       55, 43, 16, 13, "S"),
    ("parking_lot",       "Parking Lot",               72, 43, 28, 13, "S"),
    # TRAIN STATION
    ("engine_repair",     "Engine Repair",              2, 58, 11,  9, "T"),
    ("fuel_station",      "Fuel Station",              14, 58, 11,  9, "T"),
    ("electrical_bay",    "Electrical Bay",            26, 58, 12,  9, "T"),
    ("terminal_zero",     "TERMINAL\nZERO",            39, 56, 15, 11, "T"),
    ("signal_control",    "Signal Control",            55, 58, 11,  9, "T"),
    ("track_control",     "Track Control",             67, 58, 11,  9, "T"),
    ("maint_depot",       "Maintenance\nDepot",        79, 58, 15,  9, "T"),
    # TRAIN CARS
    ("locomotive",        "Locomotive",                 2, 68,  9,  8, "T"),
    ("train_car1",        "Train Car",                 12, 68, 11,  8, "T"),
    ("train_car2",        "Train Car",                 24, 68, 11,  8, "T"),
    ("train_car3",        "Train Car",                 36, 68, 11,  8, "T"),
    ("train_car4",        "Platform",                  48, 68, 11,  8, "T"),
    ("train_car5",        "Train Car",                 60, 68, 11,  8, "T"),
    ("train_car6",        "Depart Track",              72, 68, 11,  8, "T"),
]

# ── corridor connections (all rooms linked, all gates open) ────────
CONNECTIONS = [
    # zombie interior
    ("dead_end","iron_yard"),("iron_yard","rust_factory"),
    ("dead_end","scrap_depot"),("iron_yard","power_ruins"),
    ("rust_factory","shattered_wh"),("scrap_depot","power_ruins"),
    ("power_ruins","shattered_wh"),("scrap_depot","corruption_lab"),
    ("power_ruins","breach_control"),("corruption_lab","breach_control"),
    ("corruption_lab","waste_grounds"),("waste_grounds","watch_post"),
    ("watch_post","control_node"),("breach_control","control_node"),
    ("shattered_wh","control_node"),
    # through barrier — ALL OPEN
    ("rust_factory","north_breach"),("north_breach","security_hq"),
    ("dead_end","north_breach"),
    ("shattered_wh","east_breach"),("east_breach","med_bay"),
    ("control_node","south_breach"),("south_breach","comm_room"),
    ("dead_gate","generator_room"),("dead_gate","control_node"),
    # survivor interior
    ("security_hq","residential_blk"),("residential_blk","watchtower"),
    ("security_hq","med_bay"),("residential_blk","supply_hub"),
    ("watchtower","tool_shed"),("med_bay","supply_hub"),
    ("supply_hub","tool_shed"),("med_bay","generator_room"),
    ("supply_hub","central_cyard"),("tool_shed","fuel_depot"),
    ("generator_room","central_cyard"),("central_cyard","fuel_depot"),
    ("generator_room","comm_room"),("central_cyard","parking_lot"),
    ("fuel_depot","parking_lot"),
    # survivor → station
    ("comm_room","engine_repair"),("comm_room","signal_control"),
    ("parking_lot","track_control"),("parking_lot","maint_depot"),
    # station interior
    ("engine_repair","fuel_station"),("fuel_station","electrical_bay"),
    ("electrical_bay","terminal_zero"),("terminal_zero","signal_control"),
    ("signal_control","track_control"),("track_control","maint_depot"),
    # station → train
    ("terminal_zero","locomotive"),("terminal_zero","train_car3"),
    ("locomotive","train_car1"),("train_car1","train_car2"),
    ("train_car2","train_car3"),("train_car3","train_car4"),
    ("train_car4","train_car5"),("train_car5","train_car6"),
]

# ── item spawns (tx, ty, label, colour) ───────────────────────────
ITEMS = [
    (20, 7,  "⛽", (0.9,0.2,0.2,1)),
    (22,32,  "⚡", (0.1,0.6,1.0,1)),
    (24,32,  "⚡", (0.1,0.6,1.0,1)),
    (20,32,  "🔧", (0.9,0.6,0.1,1)),
    (20,17,  "⚡", (0.1,0.6,1.0,1)),
    ( 5,17,  "🔧", (0.9,0.6,0.1,1)),
    ( 5,47,  "+ ", (0.9,0.9,0.8,1)),
    (41,45,  "🔧", (0.9,0.6,0.1,1)),
    (57,18,  "+ ", (0.9,0.9,0.8,1)),
    (60,18,  "💉", (0.8,0.1,0.1,1)),
    (74,18,  "🔫", (0.7,0.7,0.7,1)),
    (90,18,  "🔫", (0.5,0.5,0.5,1)),
    (57,32,  "⛽", (0.9,0.2,0.2,1)),
    (90,32,  "⛽", (0.9,0.2,0.2,1)),
    (57, 5,  "🔦", (1.0,0.85,0.3,1)),
    (90, 5,  "🔫", (0.5,0.5,0.5,1)),
    (63,47,  "⚡", (0.1,0.6,1.0,1)),
    (15,61,  "🔧", (0.9,0.6,0.1,1)),
    (17,61,  "⛽", (0.9,0.2,0.2,1)),
    (29,61,  "⚡", (0.1,0.6,1.0,1)),
    (82,61,  "🔧", (0.9,0.6,0.1,1)),
]


def _build_grid():
    """Build fully open walkable grid — all rooms + corridors carved."""
    grid = [[WALL]*GRID_W for _ in range(GRID_H)]
    rmap = {}

    for rid, name, tx, ty, tw, th, zone in ROOMS:
        # outer wall ring
        for gy in range(ty, min(ty+th, GRID_H)):
            for gx in range(tx, min(tx+tw, GRID_W)):
                grid[gy][gx] = WALL
        # inner floor
        for gy in range(ty+1, min(ty+th-1, GRID_H)):
            for gx in range(tx+1, min(tx+tw-1, GRID_W)):
                grid[gy][gx] = FLOOR
        cx, cy = tx+tw//2, ty+th//2
        rmap[rid] = dict(tx=tx, ty=ty, tw=tw, th=th, cx=cx, cy=cy, zone=zone, name=name)

    def carve(x, y):
        for ox in range(2):
            nx, ny = x+ox, y
            if 0 < nx < GRID_W-1 and 0 < ny < GRID_H-1:
                grid[ny][nx] = FLOOR

    # carve corridors
    for a_id, b_id in CONNECTIONS:
        if a_id not in rmap or b_id not in rmap:
            continue
        a, b = rmap[a_id], rmap[b_id]
        x, y = a["cx"], a["cy"]
        tx2, ty2 = b["cx"], b["cy"]
        while x != tx2:
            carve(x, y)
            x += 1 if tx2 > x else -1
        while y != ty2:
            carve(x, y)
            y += 1 if ty2 > y else -1
        carve(tx2, ty2)

    # carve door openings
    for a_id, b_id in CONNECTIONS:
        if a_id not in rmap or b_id not in rmap:
            continue
        a, b = rmap[a_id], rmap[b_id]
        dx = b["cx"] - a["cx"]
        dy = b["cy"] - a["cy"]
        if abs(dx) >= abs(dy):
            door_x = a["tx"] + (a["tw"]-1 if dx > 0 else 0)
            door_y = a["cy"]
        else:
            door_x = a["cx"]
            door_y = a["ty"] + (a["th"]-1 if dy > 0 else 0)
        carve(door_x, door_y)

    return grid, rmap


ZONE_FLOOR = {"Z": C_FLOOR_Z, "S": C_FLOOR_S, "T": C_FLOOR_T, "B": C_FLOOR_B}
ZONE_WALL  = {"Z": C_WALL_Z,  "S": C_WALL_S,  "T": C_WALL_T,  "B": C_FLOOR_B}
ZONE_BORDER= {"Z": C_BORDER_Z,"S": C_BORDER_S, "T": C_BORDER_T,"B": C_BARRIER}


class TopDownMapWidget(Widget):
    """2-D overhead map with WASD player movement and camera follow."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._grid, self._rmap = _build_grid()

        # spawn at Security HQ
        sp = self._rmap.get("security_hq") or list(self._rmap.values())[0]
        self.px = float(sp["cx"]) + 0.5
        self.py = float(sp["cy"]) + 0.5

        self._keys = set()
        self._kb = None
        self._joy_uid = None
        self._joy_ox = self._joy_oy = 0.0
        self._joy_vx = self._joy_vy = 0.0

        self._item_alive = [True] * len(ITEMS)
        self._collected  = 0
        self._cur_room   = "Security HQ"

        # request keyboard
        self._request_kb()

        Clock.schedule_interval(self._update, 1/30)
        self.bind(size=self._redraw, pos=self._redraw)

    def _request_kb(self, *_):
        try:
            self._kb = Window.request_keyboard(self._kb_closed, self)
            self._kb.bind(on_key_down=self._kd, on_key_up=self._ku)
        except Exception:
            pass

    def _kb_closed(self):
        if self._kb:
            self._kb.unbind(on_key_down=self._kd, on_key_up=self._ku)
            self._kb = None

    def _kd(self, _kb, kc, _txt, _mods):
        self._keys.add(kc[1].lower() if isinstance(kc[1], str) else kc[1])

    def _ku(self, _kb, kc, _txt):
        self._keys.discard(kc[1].lower() if isinstance(kc[1], str) else kc[1])

    # touch joystick
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        if touch.x < self.center_x and self._joy_uid is None:
            self._joy_uid = touch.uid
            self._joy_ox, self._joy_oy = touch.x, touch.y
        return True

    def on_touch_move(self, touch):
        if touch.uid != self._joy_uid:
            return super().on_touch_move(touch)
        dx = (touch.x - self._joy_ox) / max(1, self.width*0.14)
        dy = (touch.y - self._joy_oy) / max(1, self.height*0.14)
        ln = math.hypot(dx, dy)
        if ln > 1: dx, dy = dx/ln, dy/ln
        self._joy_vx, self._joy_vy = dx, -dy
        return True

    def on_touch_up(self, touch):
        if touch.uid == self._joy_uid:
            self._joy_uid = None
            self._joy_vx = self._joy_vy = 0.0
        return super().on_touch_up(touch)

    def _solid(self, x, y):
        gx, gy = int(math.floor(x)), int(math.floor(y))
        if gx < 0 or gy < 0 or gx >= GRID_W or gy >= GRID_H:
            return True
        return self._grid[gy][gx] == WALL

    def _update(self, dt):
        dt = min(dt, 0.05)
        kx = ky = 0.0
        ks = self._keys
        if "a" in ks or "left"  in ks: kx -= 1
        if "d" in ks or "right" in ks: kx += 1
        if "w" in ks or "up"    in ks: ky -= 1
        if "s" in ks or "down"  in ks: ky += 1
        mx = kx + self._joy_vx
        my = ky + self._joy_vy
        ln = math.hypot(mx, my)
        if ln > 1: mx, my = mx/ln, my/ln
        dx, dy = mx*MOVE_SPEED*dt, my*MOVE_SPEED*dt
        r = PLAYER_RADIUS
        nx = self.px + dx
        if not (self._solid(nx-r, self.py) or self._solid(nx+r, self.py)
                or self._solid(nx, self.py-r) or self._solid(nx, self.py+r)):
            self.px = nx
        ny = self.py + dy
        if not (self._solid(self.px, ny-r) or self._solid(self.px, ny+r)
                or self._solid(self.px-r, ny) or self._solid(self.px+r, ny)):
            self.py = ny
        self.px = max(r, min(GRID_W-r, self.px))
        self.py = max(r, min(GRID_H-r, self.py))

        # item pickup
        for i, (ix, iy, lbl, col) in enumerate(ITEMS):
            if self._item_alive[i]:
                if math.hypot(self.px-(ix+0.5), self.py-(iy+0.5)) < 1.1:
                    self._item_alive[i] = False
                    self._collected += 1

        # room detection
        gx2, gy2 = int(self.px), int(self.py)
        for rid, rm in self._rmap.items():
            if (rm["tx"] <= gx2 < rm["tx"]+rm["tw"] and
                    rm["ty"] <= gy2 < rm["ty"]+rm["th"]):
                self._cur_room = rm["name"].replace("\n"," ")
                break

        self._redraw()

    def _redraw(self, *_):
        if self.width < 2 or self.height < 2:
            return

        # scale so full map fits, then follow player
        scale = min(self.width/(GRID_W*TILE), self.height/(GRID_H*TILE))
        vw = self.width  / scale
        vh = self.height / scale
        cam_x = max(0, min(GRID_W*TILE - vw, self.px*TILE - vw/2))
        cam_y = max(0, min(GRID_H*TILE - vh, self.py*TILE - vh/2))

        def scr(tx, ty):          # tile-px → screen
            return (tx - cam_x)*scale + self.x, self.top - (ty - cam_y)*scale

        def rect(tx, ty, tw=1, th=1):
            sx, sy_top = scr(tx*TILE, ty*TILE)
            return sx, sy_top - th*TILE*scale, tw*TILE*scale, th*TILE*scale

        self.canvas.clear()
        with self.canvas:
            # background
            Color(*C_BG)
            Rectangle(pos=self.pos, size=self.size)

            # zone backgrounds
            x,y,w,h = rect(0,0,50,80)
            Color(*C_FLOOR_Z); Rectangle(pos=(x,y),size=(w,h))
            x,y,w,h = rect(47,0,10,58)
            Color(*C_FLOOR_B); Rectangle(pos=(x,y),size=(w,h))
            x,y,w,h = rect(54,0,46,58)
            Color(*C_FLOOR_S); Rectangle(pos=(x,y),size=(w,h))
            x,y,w,h = rect(0,56,100,44)
            Color(*C_FLOOR_T); Rectangle(pos=(x,y),size=(w,h))

            # floor cells
            fc = int(cam_x/TILE); lc = min(GRID_W, fc + int(vw/TILE)+2)
            fr = int(cam_y/TILE); lr = min(GRID_H, fr + int(vh/TILE)+2)
            for row in range(fr, lr):
                for col in range(fc, lc):
                    if self._grid[row][col] == FLOOR:
                        zone = "S"
                        for _, _n, tx, ty, tw, th, z in ROOMS:
                            if tx<=col<tx+tw and ty<=row<ty+th:
                                zone = z; break
                        Color(*ZONE_FLOOR.get(zone, C_FLOOR_S))
                        sx, sy = scr(col*TILE, row*TILE)
                        ps = TILE*scale+1
                        Rectangle(pos=(sx, sy-ps), size=(ps, ps))

            # room borders + labels
            font = None
            try:
                from kivy.core.text import Label as KLabel
            except Exception:
                KLabel = None

            for rid, name, tx, ty, tw, th, zone in ROOMS:
                rx, ry, rw, rh = rect(tx, ty, tw, th)
                Color(*ZONE_BORDER.get(zone, C_BORDER_S))
                Line(rectangle=(rx, ry, rw, rh), width=max(1.0, 1.5*scale*TILE/8))

            # red barrier wall
            wx, _ = scr(49*TILE, 0)
            Color(*C_BARRIER)
            Line(points=[wx, self.y, wx, self.top], width=max(2, int(3*scale*TILE/8)))

            # yellow hazard stripes
            Color(*C_STRIPE)
            for sr in range(0, 56, 5):
                sx2, sy_top2 = scr(47*TILE, sr*TILE)
                sw2 = 5*TILE*scale
                sh2 = 1.5*TILE*scale
                Rectangle(pos=(sx2, sy_top2-sh2*0.35), size=(sw2, sh2*0.3))

            # breach labels
            for bname, bx, by in [
                ("NORTH BREACH", 49, 2),
                ("EAST BREACH",  49,20),
                ("SOUTH BREACH", 49,40),
            ]:
                bsx, bsy = scr((bx+2.5)*TILE, (by+3.5)*TILE)
                Color(0.8, 0.08, 0.08, 0.85)
                Rectangle(pos=(bsx-28*scale, bsy-8*scale), size=(56*scale, 14*scale))

            # items
            for i, (ix, iy, lbl, col) in enumerate(ITEMS):
                if not self._item_alive[i]: continue
                sx2, sy2 = scr((ix+0.5)*TILE, (iy+0.5)*TILE)
                rr = max(4, 7*scale)
                Color(col[0],col[1],col[2],0.28)
                Ellipse(pos=(sx2-rr*1.7,sy2-rr*1.7),size=(rr*3.4,rr*3.4))
                Color(*col)
                Ellipse(pos=(sx2-rr,sy2-rr),size=(rr*2,rr*2))
                Color(0,0,0,0.6)
                Ellipse(pos=(sx2-rr*0.55,sy2-rr*0.55),size=(rr*1.1,rr*1.1))

            # player shadow
            psx, psy = scr(self.px*TILE, self.py*TILE)
            pr = max(6, PLAYER_RADIUS*TILE*scale)
            Color(0,0,0,0.3)
            Ellipse(pos=(psx-pr*1.1,psy-pr*1.4),size=(pr*2.2,pr*1.5))
            # player body
            Color(*C_PLAYER)
            Ellipse(pos=(psx-pr,psy-pr),size=(pr*2,pr*2))
            # player outline
            Color(0.3,0.25,0.05,1)
            Line(circle=(psx,psy,pr), width=1.5)
            # direction dot
            Color(0.15,0.10,0.0,1)
            Ellipse(pos=(psx-pr*0.22,psy-pr*0.22),size=(pr*0.44,pr*0.44))

            # map border
            Color(*C_BARRIER)
            Line(rectangle=(self.x+1,self.y+1,self.width-2,self.height-2), width=2)

    def get_location(self): return self._cur_room
    def get_collected(self): return self._collected

    def cleanup(self):
        self._kb_closed()
        Clock.unschedule(self._update)


class TopDownScreen(BoxLayout):
    """Full-screen wrapper: HUD + 2-D map + hint footer."""

    def __init__(self, on_back, **kwargs):
        super().__init__(orientation="vertical",
                         spacing=dp(3), padding=(dp(5),dp(3)), **kwargs)
        self._on_back = on_back

        # header
        hdr = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self._loc  = Label(text="📍 Security HQ", bold=True,
                           color=(0.95,0.92,0.85,1), halign="left", valign="middle")
        self._loc.bind(size=lambda w,s: setattr(w,"text_size",s))
        self._items = Label(text="🎒 0", bold=True, size_hint_x=0.22,
                            color=(0.3,0.9,0.4,1), halign="right", valign="middle")
        self._items.bind(size=lambda w,s: setattr(w,"text_size",s))
        btn = Button(text="MENU", size_hint_x=None, width=dp(72),
                     background_color=(0.45,0.07,0.07,1))
        btn.bind(on_release=lambda *_: self._exit())
        hdr.add_widget(self._loc)
        hdr.add_widget(self._items)
        hdr.add_widget(btn)
        self.add_widget(hdr)

        # map
        self._map = TopDownMapWidget()
        self.add_widget(self._map)

        # footer
        ftr = BoxLayout(size_hint_y=None, height=dp(34))
        hint = Label(text="WASD / Arrow keys to move   |   Touch: left-side joystick",
                     color=(0.6,0.65,0.68,1), font_size="11sp",
                     halign="center", valign="middle")
        hint.bind(size=lambda w,s: setattr(w,"text_size",s))
        ftr.add_widget(hint)
        self.add_widget(ftr)

        self._hud = Clock.schedule_interval(self._tick_hud, 0.2)

    def _tick_hud(self, _dt):
        self._loc.text   = "📍 " + self._map.get_location()
        self._items.text = f"🎒 {self._map.get_collected()}"

    def _exit(self):
        Clock.unschedule(self._hud)
        self._map.cleanup()
        self._on_back()

    def on_parent(self, widget, parent):
        if parent is None:
            Clock.unschedule(self._hud)
            self._map.cleanup()
