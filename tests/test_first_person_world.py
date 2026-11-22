import math
from redline.gameplay.map_data import load_map_layout
from redline.gameplay.raycast_world import (
    GRID_H, GRID_W, build_world, cast_ray, is_solid, move_player,
)


def test_first_person_world_contains_all_authored_locations():
    world = build_world(load_map_layout())
    assert len(world["rooms"]) == 39
    assert "terminal_zero" in world["rooms"]
    assert "passenger_platform" in world["rooms"]
    assert "safe_haven" in world["rooms"]


def test_every_location_is_reachable_from_survivor_spawn():
    world = build_world(load_map_layout())
    grid = world["grid"]
    sx, sy = map(int, world["spawn"])
    queue = [(sx, sy)]
    seen = {(sx, sy)}
    while queue:
        x, y = queue.pop(0)
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H and not grid[ny][nx] and (nx,ny) not in seen:
                seen.add((nx,ny))
                queue.append((nx,ny))
    for room in world["rooms"].values():
        assert (room["cx"], room["cy"]) in seen, f"Unreachable room: {room['name']}"


def test_collision_blocks_walls_and_keeps_player_in_world():
    world = build_world(load_map_layout())
    x, y = world["spawn"]
    assert not is_solid(world, x, y)
    nx, ny = move_player(world, x, y, 0.15, 0.0)
    assert not is_solid(world, nx, ny)
    assert is_solid(world, -1, -1)


def test_turning_changes_ray_direction_and_raycast_hits_wall():
    world = build_world(load_map_layout())
    x, y = world["spawn"]
    d1, _ = cast_ray(world, x, y, math.radians(-90))
    d2, _ = cast_ray(world, x, y, math.radians(0))
    assert d1 > 0 and d2 > 0
    assert abs(d1 - d2) > 0.01


def test_player_can_move_inside_room_without_crossing_its_wall():
    world = build_world(load_map_layout())
    x, y = world["spawn"]
    for _ in range(10):
        x, y = move_player(world, x, y, 0.05, 0.0)
    assert not is_solid(world, x, y)
