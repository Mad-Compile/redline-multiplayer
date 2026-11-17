"""Source-derived REDLINE MAP 01 layout data.

The payload is the original map package's scene_data.py metadata, compressed
for the Android bundle. It retains all 39 locations, zone tile coordinates,
room descriptions, loot, exits, spawn points and survivor objectives.
"""
from __future__ import annotations

import base64
import gzip
import json
from functools import lru_cache

_MAP_LAYOUT_GZIP_B64 = (
    "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"
)

@lru_cache(maxsize=1)
def load_map_layout() -> dict:
    """Return the exact source-derived REDLINE MAP 01 layout."""
    payload = gzip.decompress(base64.b64decode(_MAP_LAYOUT_GZIP_B64))
    layout = json.loads(payload.decode("utf-8"))
    _validate_layout(layout)
    return layout


def _validate_layout(layout: dict) -> None:
    scenes = layout.get("scenes", [])
    ids = {scene.get("id") for scene in scenes}
    if len(scenes) != 39 or len(ids) != len(scenes):
        raise ValueError("REDLINE MAP 01 must contain 39 uniquely named locations")
    for scene in scenes:
        x, y = scene["tile_x"], scene["tile_y"]
        w, h = scene["tile_w"], scene["tile_h"]
        if x < 0 or y < 0 or w < 1 or h < 1 or x + w > 128 or y + h > 100:
            raise ValueError(f"Location outside map bounds: {scene.get('id')}")
        for connected in scene.get("exits", []) + scene.get("connects", []):
            if connected not in ids:
                raise ValueError(f"Unknown map connection: {scene.get('id')} -> {connected}")
