from redline.settings import (
    DEFAULT_PREFERENCES,
    SELECT_OPTIONS,
    load_preferences,
    save_preferences,
)


def test_default_settings_match_the_redline_ui_choices(tmp_path):
    preferences = load_preferences(tmp_path / "missing.json")
    assert preferences == DEFAULT_PREFERENCES
    assert preferences["resolution"] in SELECT_OPTIONS["resolution"]
    assert preferences["shadows"] in SELECT_OPTIONS["shadows"]


def test_settings_preferences_persist_and_restore(tmp_path):
    path = tmp_path / "settings" / "redline_settings.json"
    changed = dict(DEFAULT_PREFERENCES)
    changed.update({
        "master_volume": 0.37,
        "music_volume": 0.22,
        "sfx_volume": 0.81,
        "resolution": "85%",
        "shadows": "Low",
        "player_names": "Off",
        "control_stick": "Fixed",
        "control_device": "Controller",
    })
    save_preferences(path, changed)
    restored = load_preferences(path)
    assert restored == changed


def test_invalid_saved_values_fall_back_to_safe_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(
        '{"master_volume": 4, "music_volume": -1, "resolution": "999%", "shadows": "Ultra"}',
        encoding="utf-8",
    )
    restored = load_preferences(path)
    assert restored["master_volume"] == 1.0
    assert restored["music_volume"] == 0.0
    assert restored["resolution"] == DEFAULT_PREFERENCES["resolution"]
    assert restored["shadows"] == DEFAULT_PREFERENCES["shadows"]
