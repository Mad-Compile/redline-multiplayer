# REDLINE

REDLINE is an Android-first, isometric 2D multiplayer survival game. The active development direction on this branch is **Python + Kivy**.

## Active Python migration

- Python 3.11+
- Kivy 2.3.1 for 2D rendering, touch UI and Android lifecycle
- Pillow for reading the supplied WebP artwork
- Buildozer / python-for-android for Android APK/AAB packaging
- GitHub Actions for automated validation and Android builds

The Godot files and earlier branches are retained as historical source material. They are no longer the active runtime for this branch.

## Preserved supplied artwork

The original menu artwork archive is retained unchanged at `assets/menu/menu_art.zip`. The Python menu reads its original four WebP files and converts runtime copies for Kivy; it does not replace the supplied artwork with generated shapes.

See [the asset inventory](docs/PYTHON_ASSET_INVENTORY.md) and [the migration status](PYTHON_MIGRATION.md).

## Current gameplay direction

- Survivors and Dead (Zombies) start in separate territories divided by a wall.
- Zombies complete objectives to weaken and breach the wall.
- Survivors complete objectives to prepare the train for escape.
- Zombies entering survivor territory after the breach trigger HUNT.
- Zombie attacks use a cooldown.
- Survivors are knocked down for 20 seconds and can be revived during that window.

## Run

Desktop:
`python -m pip install -r requirements.txt`
`python main.py`

Android:
`buildozer android debug`

The Python validation workflow checks compilation, Kivy imports and gameplay-rule tests. An APK is not claimed until the Android workflow produces a real artifact. A successful build is not a substitute for gameplay testing on a device.
