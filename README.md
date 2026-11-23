# REDLINE

REDLINE is an Android-first, isometric 2D multiplayer survival game. The active runtime is **Python + Kivy**, and **main** is the single development branch.

## Runtime and Android target

- Python 3.11+
- Kivy 2.3.1 for 2D rendering, touch UI and Android lifecycle
- Pillow for decoding supplied WebP artwork
- Buildozer / python-for-android for Android APK packaging
- GitHub Actions for Python validation and Android builds

## Supplied artwork

The main menu uses the standalone supplied background at `assets/menu/menu_background.webp`, the recovered original Practice and Start Match buttons in `assets/menu/menu_buttons_recovered.zip`, and the supplied Settings gear at `assets/ui/settings/settings_gear.webp`. The settings screen also uses the supplied back and arrow artwork. The original `menu_art.zip` archive remains preserved unchanged.

The menu can play the REDLINE theme song from `assets/audio/Redline Theme Song.mp3` when that file is present. The uploaded MP3 has not yet been committed to this repository.

See [the asset inventory](docs/PYTHON_ASSET_INVENTORY.md) and [the implementation status](PYTHON_MIGRATION.md).

## Current gameplay direction

- Survivors and Dead (Zombies) begin in separate territories divided by a wall.
- Zombies complete objectives to weaken and breach the wall.
- Survivors complete objectives to prepare the train for escape.
- Zombies entering survivor territory after the breach trigger HUNT.
- Zombie attacks use a cooldown.
- Survivors are knocked down for 20 seconds and can be revived during that window.

## Current implementation status

The app currently includes the Kivy application bootstrap, illustrated main menu, persistent settings, a source-derived 39-location MAP 01 browser, and tested engine-independent match rules for preparation/breach/hunt phases, wall damage, team-locked objectives, attack cooldowns, knockdown and revival.

The MAP 01 browser is a schematic location browser, not a fully walkable playable level. Character movement and animation, zombie navigation/AI, collision, the gameplay HUD, train boarding/extraction, authoritative networking and a complete multiplayer session remain outstanding. Production artwork is not replaced with procedural placeholders.

## Run

Desktop development:

    python -m pip install -r requirements.txt
    python main.py

Android:

    buildozer android debug

Pushes to **main** run Python validation and the arm64 Android debug APK workflow. A successful CI build proves compilation and packaging, not a successful on-device gameplay session. The APK still needs installation and device testing.

## Repository workflow

All active development lands directly on **main**. There is no separate engine or migration branch in the intended workflow.
