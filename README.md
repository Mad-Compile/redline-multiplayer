# REDLINE

REDLINE is an Android-first zombie-survival game. The current exploration direction is **first-person 2.5D**: a ray-cast view rendered from a 2D tile/collision grid. The active runtime is **Python + Kivy**, and **main** is the single development branch.

## Game specification

The full project scope, controls, MAP 01 requirements, gameplay loop, multiplayer target, implementation tracker and playability quality gates are documented in [docs/GAME_SPECIFICATION.md](docs/GAME_SPECIFICATION.md).

## Runtime and Android target

- Python 3.11+
- Kivy 2.3.1 for rendering, touch UI and Android lifecycle
- Pillow for decoding supplied WebP artwork
- Buildozer / python-for-android for Android APK packaging
- GitHub Actions for Python validation and Android builds

## Supplied artwork

The main menu uses the standalone supplied background at `assets/menu/menu_background.webp`, the recovered original Practice and Start Match buttons in `assets/menu/menu_buttons_recovered.zip`, and the supplied Settings gear at `assets/ui/settings/settings_gear.webp`. The settings screen also uses the supplied back and arrow artwork. The original `menu_art.zip` archive remains preserved unchanged.

See [the asset inventory](docs/PYTHON_ASSET_INVENTORY.md) and [the implementation status](PYTHON_MIGRATION.md).

## Current gameplay direction

- Survivors and Dead (Zombies) begin in separate territories divided by a wall.
- Zombies complete objectives to weaken and breach the wall.
- Survivors complete objectives to prepare the train for escape.
- Zombies entering survivor territory after the breach trigger HUNT.
- Zombie attacks use a cooldown.
- Survivors are knocked down for 20 seconds and can be revived during that window.

## Current implementation status

The app includes the Kivy application bootstrap, illustrated main menu, persistent settings, source-derived 39-location MAP 01 data, a first-person 2.5D ray-cast exploration foundation, generated room/corridor grid, basic movement and collision, mobile joystick/swipe-look input, and automated tests for world connectivity, movement, collision and ray casting. Engine-independent match rules cover preparation/breach/hunt phases, wall damage, team-locked objectives, attack cooldowns, knockdown and revival.

This is an exploration prototype, not a finished game. Detailed building interiors matching the supplied artwork, production environment textures, complete door/object interactions, polished zombie AI/animation/audio, the full objective-to-train extraction loop, authoritative online multiplayer and full real-device gameplay QA remain outstanding. A CI APK build proves packaging, not complete playability.

## Run

Desktop development:

    python -m pip install -r requirements.txt
    python main.py

Android:

    buildozer android debug

Pushes to **main** run Python validation and the arm64 Android debug APK workflow. The APK still needs installation and device testing.

## Repository workflow

All active development lands directly on **main**. There is no separate engine or migration branch in the intended workflow.
