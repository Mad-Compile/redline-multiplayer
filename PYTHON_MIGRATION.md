# REDLINE Python migration

Active migration branch: `python/kivy-migration`

## Runtime and Android target

- Python 3.11+
- Kivy 2.3.1 for rendering, touch UI and Android application lifecycle
- Buildozer / python-for-android for Android APK/AAB packaging
- Pillow for decoding the supplied WebP menu artwork on Android

Kivy is selected over Pygame-CE because REDLINE's required deliverable is a native Android app and Kivy maintains an Android packaging path.

## Preserved production assets

The original menu artwork archive remains at `assets/menu/menu_art.zip`. The Python menu reads the four original WebP files from that archive and converts copies to PNG in the app's writable cache; it does not alter the archive.

The uploaded REDLINE theme song is available in the conversation workspace but has not yet been committed into this branch. The menu supports it at `assets/audio/Redline Theme Song.mp3` once copied into the repository.

The Gemini map package is not yet fully portable: the staging branch contains its scene and gameplay scripts, but its referenced `redline_iso_atlas.webp` and `redline_structures_sheet.webp` are absent from that branch. The Python migration must not replace those missing production images with generated geometry. Recover the original image files before building the final map renderer.

## Current Python work

- Kivy application bootstrap and image-backed main menu
- Recovery and loading of the three intact original menu button images
- Functional settings volume control when theme audio is present
- Explicitly honest Practice / Multiplayer notices until those systems are connected
- Engine-independent match rules ported from the supplied Gemini scripts:
  - preparation / breach / hunt phase transitions
  - armored destructible wall segments
  - team-locked objective work
  - 2.5-second zombie attack cooldown
  - 20-second survivor knockdown deadline
  - 3.5-second revive channel
  - survivor train-objective completion state
- Automated unit tests for the rules

## Not yet implemented

Character art and animation integration, player movement, zombie navigation/AI, collision, mobile gameplay HUD, train boarding/escape, authoritative network transport/lobby, and final map rendering remain outstanding. This branch is a migration foundation, not a playable release.

## Build

Desktop development:
`python -m pip install -r requirements.txt && python main.py`

Android:
`buildozer android debug`

The repository's GitHub Actions workflow currently runs syntax compilation and deterministic gameplay-rule tests. An Android APK is not claimed until an Android build workflow has run successfully and produced an artifact.
