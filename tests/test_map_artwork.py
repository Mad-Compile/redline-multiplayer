"""Regression tests for the original flat-map white-screen failure."""
from redline.gameplay.map_data import load_map_layout
from redline.gameplay.raycast_world import build_world, GRID_H, GRID_W


def test_authored_map_data_drives_playable_world_not_a_flat_image():
    layout = load_map_layout()
    world = build_world(layout)
    assert len(layout["scenes"]) == 39
    assert len(world["rooms"]) == 39
    assert len(world["grid"]) == GRID_H
    assert all(len(row) == GRID_W for row in world["grid"])
    assert "safe_haven" in world["rooms"]
    assert "terminal_zero" in world["rooms"]
    assert "departure_track" in world["rooms"]
