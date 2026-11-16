from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

ARTWORK = {
    "assets/menu/practice_button.webp",
    "assets/menu/start_match_button.webp",
    "assets/menu/settings_button.webp",
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
