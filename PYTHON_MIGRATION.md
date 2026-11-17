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

### User-supplied MAP 01 package

The user uploaded `REDLINE_MAP01_Python.zip`. Its ZIP integrity check passes and it contains the full-map overview, four zone exports, 39 room/scene cards, the Pillow map renderer, and the source scene definitions.

- `redline/gameplay/map_data.py` now contains the source-derived layout metadata: 128×100 tiles, 32px source tile size, all 39 room/breach/railway locations, room coordinates, loot, exits, spawn points, and the eight survivor escape objectives.
- `redline/gameplay/map_screen.py` provides an interactive room/location browser from those authored coordinates. The Practice menu button now opens this Map 01 browser.
- CI validates all 39 location IDs and graph connections and instantiates the map viewer under Xvfb.
- The source package has an internal count mismatch: its README/overview text says 33 scenes, but its data defines 39 (9 + 8 + 12 + 10) and the archive contains 39 scene cards. The integrated data follows the actual source definitions and uses 39.
- The map browser is a schematic location/layout view, not a finished walkable environment or playable level. The source map PNG and individual scene-card PNGs are not yet loaded as in-game environmental textures. No claim is made that terrain art, collision, actors, or character movement are complete.

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
