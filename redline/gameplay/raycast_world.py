"""REDLINE first-person 2.5D world generated from the authored MAP 01 grid.

Rooms use the exact tile bounds and names in map_data.py. Corridors connect
all authored locations; doors are traversable openings, and collision is
resolved against the same grid used by the ray caster.
"""
from __future__ import annotations

import math

GRID_W, GRID_H = 128, 100
WALL = 1
FLOOR = 0
FOV = math.radians(66)
PLAYER_RADIUS = 0.19


def build_world(layout):
    """Build a connected tile world from all 39 source-defined locations."""
    grid = [[WALL for _ in range(GRID_W)] for _ in range(GRID_H)]
    rooms = {}
    scenes = layout.get("scenes", [])
    for scene in scenes:
        x, y = int(scene["tile_x"]), int(scene["tile_y"])
        w, h = int(scene["tile_w"]), int(scene["tile_h"])
        # Every location gets an enclosed, walkable interior with a real wall.
        for gy in range(y, min(y + h, GRID_H)):
            for gx in range(x, min(x + w, GRID_W)):
                grid[gy][gx] = WALL
        for gy in range(y + 1, min(y + h - 1, GRID_H)):
            for gx in range(x + 1, min(x + w - 1, GRID_W)):
                grid[gy][gx] = FLOOR
        rooms[scene["id"]] = {
            "name": scene["name"], "x": x, "y": y, "w": w, "h": h,
            "cx": x + w // 2, "cy": y + h // 2,
            "zone": scene.get("zone", "D"),
        }

    # Build the authored connection graph, then connect any intentionally
    # unlinked rooms to their nearest neighbour so every location is reachable.
    ids = set(rooms)
    edges = set()
    for scene in scenes:
        a = scene["id"]
        for b in scene.get("exits", []) + scene.get("connects", []):
            if b in ids and a != b:
                edges.add(tuple(sorted((a, b))))
    degree = {sid: sum(sid in edge for edge in edges) for sid in ids}
    # The authored graph contains deliberate one-way/isolated utility rooms.
    # Add a stable neighbour chain so every authored location is reachable.
    for index in range(len(scenes) - 1):
        edges.add(tuple(sorted((scenes[index]["id"], scenes[index + 1]["id"]))))
    for sid in ids:
        if degree[sid] == 0:
            a = rooms[sid]
            nearest = min((other for other in ids if other != sid),
                          key=lambda other: (rooms[other]["cx"]-a["cx"])**2 +
                                            (rooms[other]["cy"]-a["cy"])**2)
            edges.add(tuple(sorted((sid, nearest))))

    def carve(x, y):
        if 1 <= x < GRID_W - 1 and 1 <= y < GRID_H - 1:
            grid[y][x] = FLOOR
            if x + 1 < GRID_W - 1:
                grid[y][x + 1] = FLOOR

    for a_id, b_id in sorted(edges):
        a, b = rooms[a_id], rooms[b_id]
        x, y = a["cx"], a["cy"]
        tx, ty = b["cx"], b["cy"]
        # A deterministic L-shaped corridor with two-tile width.
        while x != tx:
            carve(x, y)
            x += 1 if tx > x else -1
        while y != ty:
            carve(x, y)
            y += 1 if ty > y else -1
        carve(tx, ty)

    # Ensure doors in each room's boundary toward a connected neighbour.
    for a_id, b_id in edges:
        a, b = rooms[a_id], rooms[b_id]
        dx, dy = b["cx"] - a["cx"], b["cy"] - a["cy"]
        if abs(dx) >= abs(dy):
            door_x = a["x"] + (a["w"] - 1 if dx > 0 else 0)
            door_y = a["cy"]
        else:
            door_x = a["cx"]
            door_y = a["y"] + (a["h"] - 1 if dy > 0 else 0)
        carve(door_x, door_y)

    spawn = next((s for s in scenes if s.get("spawn") == "survivor"), None)
    if spawn is None:
        spawn = next((s for s in scenes if s["id"] == "safe_haven"), scenes[0])
    player = (rooms[spawn["id"]]["cx"] + 0.5, rooms[spawn["id"]]["cy"] + 0.5)
    return {"grid": grid, "rooms": rooms, "edges": edges, "spawn": player}


def is_solid(world, x, y):
    gx, gy = int(math.floor(x)), int(math.floor(y))
    if gx < 0 or gy < 0 or gx >= GRID_W or gy >= GRID_H:
        return True
    return world["grid"][gy][gx] == WALL


def move_player(world, x, y, dx, dy, radius=PLAYER_RADIUS):
    """Axis-separated circle-ish collision keeps the player out of wall corners."""
    nx = x + dx
    if not (is_solid(world, nx-radius, y) or is_solid(world, nx+radius, y) or
            is_solid(world, nx, y-radius) or is_solid(world, nx, y+radius)):
        x = nx
    ny = y + dy
    if not (is_solid(world, x-radius, ny) or is_solid(world, x+radius, ny) or
            is_solid(world, x, ny-radius) or is_solid(world, x, ny+radius)):
        y = ny
    return x, y


def current_location(world, x, y):
    gx, gy = int(x), int(y)
    for sid, room in world["rooms"].items():
        if room["x"] <= gx < room["x"] + room["w"] and room["y"] <= gy < room["y"] + room["h"]:
            return room["name"]
    return "OUTER CORRIDOR"


def cast_ray(world, px, py, angle, max_depth=32.0):
    """Grid DDA ray cast. Returns corrected distance and wall side."""
    ray_dx, ray_dy = math.cos(angle), math.sin(angle)
    map_x, map_y = int(px), int(py)
    delta_x = abs(1.0 / ray_dx) if abs(ray_dx) > 1e-9 else 1e9
    delta_y = abs(1.0 / ray_dy) if abs(ray_dy) > 1e-9 else 1e9
    if ray_dx < 0:
        step_x, side_x = -1, (px - map_x) * delta_x
    else:
        step_x, side_x = 1, (map_x + 1.0 - px) * delta_x
    if ray_dy < 0:
        step_y, side_y = -1, (py - map_y) * delta_y
    else:
        step_y, side_y = 1, (map_y + 1.0 - py) * delta_y
    side = 0
    for _ in range(96):
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
            distance = side_x - delta_x
        else:
            side_y += delta_y
            map_y += step_y
            side = 1
            distance = side_y - delta_y
        if distance > max_depth:
            return max_depth, side
        if map_x < 0 or map_y < 0 or map_x >= GRID_W or map_y >= GRID_H:
            return max(0.05, distance), side
        if world["grid"][map_y][map_x] == WALL:
            return max(0.05, distance), side
    return max_depth, side
