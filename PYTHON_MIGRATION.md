# REDLINE — Python runtime and implementation status

**Active development branch: `main`**

## Runtime and Android target

- Python 3.11+
- Kivy 2.3.1 for rendering, touch UI and Android application lifecycle
- Buildozer / python-for-android for Android APK packaging
- Pillow for decoding the supplied WebP artwork on Android

Kivy is the rendering and Android application layer. The repository's source of truth is the Python application under `redline/`, launched by `main.py`.

## Preserved production assets

- The original menu archive remains unchanged at `assets/menu/menu_art.zip`.
- The supplied standalone menu background is loaded from `assets/menu/menu_background.webp`.
- The three intact original menu button images are preserved in `assets/menu/menu_buttons_recovered.zip`; the Practice and Start Match buttons use those source images.
- The supplied Settings gear is loaded from `assets/ui/settings/settings_gear.webp`.
- Supplied Settings back/arrow images are retained under `assets/ui/settings/`.
- The uploaded REDLINE theme song is available in the conversation workspace but has not yet been committed here. The menu looks for `assets/audio/Redline Theme Song.mp3` and plays it when present.

## User-supplied MAP 01 package

The uploaded `REDLINE_MAP01_Python.zip` was inspected. Its ZIP integrity passes and it contains the full-map overview, four zone exports, 39 room/scene cards, a map renderer and source scene definitions.

- `redline/gameplay/map_data.py` contains source-derived layout metadata: 128×100 tiles, 32px source tile size, 39 room/breach/railway locations, room coordinates, loot, exits, spawn points and eight survivor escape objectives.
- `redline/gameplay/map_screen.py` provides an interactive room/location browser from those authored coordinates. The Practice menu button opens this browser.
- Automated checks validate all 39 location IDs and graph connections and instantiate the map viewer.
- The source package has a count mismatch: its README/overview text says 33 scenes, but its data defines 39 (9 + 8 + 12 + 10) and the archive contains 39 scene cards. The integrated data follows the source definitions and uses 39.
- The browser is a schematic location/layout view, not a finished walkable environment or playable level. The source map overview and individual scene-card images are not yet loaded as in-game environmental textures. Terrain rendering, collision, actors and character movement remain incomplete.

## Implemented Python systems

- Kivy application bootstrap and image-backed main menu
- Recovered original menu button artwork and supplied Settings artwork
- Persistent settings with three volume controls and five selectors
- Settings navigation and preferences persistence
- Source-derived MAP 01 location browser
- Engine-independent match rules for preparation / breach / hunt phase transitions
- Armored destructible wall segments and team-locked objective work
- 2.5-second zombie attack cooldown
- 20-second survivor knockdown deadline
- 3.5-second revive channel
- Survivor train-objective completion state
- Automated unit tests and headless UI smoke checks

## Not yet implemented

Character art and animation integration, player movement, zombie navigation/AI, collision, mobile gameplay HUD, train boarding/escape, authoritative network transport/lobby and final walkable map rendering remain outstanding. The current branch is a development foundation, not a complete playable release.

## Validation and Android build

The Python validation workflow compiles the source, imports the Kivy app, instantiates the menu, settings and MAP 01 browser under a virtual display, and runs the automated tests.

The Android workflow uses Buildozer / python-for-android to package an arm64 debug APK. CI success verifies the build pipeline; it does not replace installation and gameplay testing on an Android device.
