from pathlib import Path

from PIL import Image

from redline.gameplay.explore_screen import MAP_IMAGE_PATH, WORLD_H, WORLD_W


def test_exploration_uses_the_supplied_train_escape_map_artwork():
    assert MAP_IMAGE_PATH.is_file()
    with Image.open(MAP_IMAGE_PATH) as image:
        assert image.format == "JPEG"
        assert image.width == 256
        assert image.height == 171
    assert WORLD_W / WORLD_H == 1.5


def test_map_artwork_is_inside_android_source_bundle():
    repo_root = Path(__file__).resolve().parents[1]
    assert MAP_IMAGE_PATH == repo_root / "assets" / "maps" / "redline_train_escape.jpg"
