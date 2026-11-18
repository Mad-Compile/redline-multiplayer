from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

ARTWORK = {
    "assets/menu/practice_button.webp",
    "assets/menu/start_match_button.webp",
    "assets/menu/settings_button.webp",
}
SETTINGS_ARTWORK = {
    "assets/ui/settings/back_button.webp",
    "assets/ui/settings/arrow_left.webp",
    "assets/ui/settings/arrow_right.webp",
}


def test_recovered_archive_contains_all_three_intact_original_buttons():
    archive_path = (
        Path(__file__).resolve().parents[1]
        / "assets" / "menu" / "menu_buttons_recovered.zip"
    )
    assert archive_path.is_file()
    with ZipFile(archive_path) as archive:
        assert ARTWORK == set(archive.namelist())
        for member in ARTWORK:
            with Image.open(BytesIO(archive.read(member))) as artwork:
                artwork.verify()


def test_original_archive_is_preserved_for_recovery():
    original = (
        Path(__file__).resolve().parents[1]
        / "assets" / "menu" / "menu_art.zip"
    )
    assert original.is_file()
    assert original.stat().st_size == 26250


def test_supplied_settings_navigation_artwork_is_present_and_valid():
    project_root = Path(__file__).resolve().parents[1]
    for relative_path in SETTINGS_ARTWORK:
        asset_path = project_root / relative_path
        assert asset_path.is_file(), relative_path
        with Image.open(asset_path) as artwork:
            assert artwork.format == "WEBP"
            assert artwork.mode == "RGBA"
            assert artwork.size == (256, 256)
            artwork.verify()



def test_supplied_rusty_settings_gear_is_present_and_transparent():
    gear = (
        Path(__file__).resolve().parents[1]
        / "assets" / "ui" / "settings" / "settings_gear.webp"
    )
    assert gear.is_file()
    with Image.open(gear) as artwork:
        assert artwork.format == "WEBP"
        assert artwork.mode == "RGBA"
        assert artwork.size == (192, 192)
        # verify() alone skips pixel decoding on some Pillow/WebP builds.
        # Force the full frame decode; this catches the exact startup crash.
        artwork.load()
        assert getattr(artwork, "n_frames", 1) == 1
        assert artwork.getpixel((0, 0))[3] == 0
        artwork.verify()


def test_supplied_menu_background_fully_decodes_before_android_startup():
    background = (
        Path(__file__).resolve().parents[1]
        / "assets" / "menu" / "menu_background.webp"
    )
    assert background.is_file()
    with Image.open(background) as artwork:
        assert artwork.format == "WEBP"
        assert artwork.width > 0 and artwork.height > 0
        artwork.load()
        artwork.convert("RGBA").getpixel((0, 0))
        artwork.verify()
