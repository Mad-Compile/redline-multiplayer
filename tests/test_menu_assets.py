from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

ARTWORK = {
    "assets/menu/menu_background.webp",
    "assets/menu/practice_button.webp",
    "assets/menu/start_match_button.webp",
    "assets/menu/settings_button.webp",
}


def test_supplied_menu_archive_contains_all_original_images():
    archive_path = Path(__file__).resolve().parents[1] / "assets" / "menu" / "menu_art.zip"
    assert archive_path.is_file(), "Original supplied menu archive must be preserved"
    with ZipFile(archive_path) as archive:
        assert ARTWORK.issubset(set(archive.namelist()))
        for member in ARTWORK:
            with Image.open(BytesIO(archive.read(member))) as artwork:
                artwork.verify()
