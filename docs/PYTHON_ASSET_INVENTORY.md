# REDLINE — Python asset inventory

Inventory reconciled against the active `main` branch and available user uploads on 18 November 2026.

| Asset / source | Source / repository path | Status |
|---|---|---|
| Main-menu background | `assets/menu/menu_background.webp` | Present in the repository and loaded by the Python main menu. |
| Practice / Start Match button art | `assets/menu/menu_buttons_recovered.zip` | Two original supplied button images are recovered byte-for-byte and loaded by the menu. |
| Original menu source archive | `assets/menu/menu_art.zip` | Preserved unchanged. Its ZIP directory/final background entry was previously found incomplete; the standalone background file is retained separately. |
| Settings gear | `assets/ui/settings/settings_gear.webp` | Supplied artwork is loaded by the menu. CI forces a full pixel decode and checks alpha transparency. |
| Settings navigation artwork | `assets/ui/settings/back_button.webp`, `arrow_left.webp`, `arrow_right.webp` | Supplied images are retained and used by the illustrated settings UI. |
| REDLINE Theme Song.mp3 | Uploaded conversation file | Available in the workspace but not yet committed under `assets/audio/`. The menu has an optional playback hook for `assets/audio/Redline Theme Song.mp3`. |
| REDLINE MAP 01 Python package | User upload `REDLINE_MAP01_Python.zip` (48 entries; ZIP integrity passes) | Source archive inspected. Contains a 4096×3200 overview, four zone images, 39 512×512 scene cards, renderer and scene metadata. Source raster exports are not yet in the repository. |
| MAP 01 room layout / connections / spawn points / objectives | `redline/gameplay/map_data.py` | Integrated as source-derived data: 39 locations, 128×100 tile layout, exits, loot tables, two spawn points and eight survivor objectives. Automated validation added. |
| MAP 01 browser | `redline/gameplay/map_screen.py`; Practice menu action | Integrated as a scrollable, tappable schematic location browser. It displays authored room coordinates and metadata. It is not a playable level. |
| Original MAP 01 overview and zone PNGs | Inside the supplied MAP 01 upload | Received and inspected, but not yet bundled as in-game environmental textures. |
| Original MAP 01 scene-card PNGs | `output/scenes/scene_*.png` inside the supplied upload | 39 images received and inspected; not yet displayed in-game. |
| Gemini map package | Earlier user-supplied package | Separate from the Python MAP 01 upload. The earlier source atlas and structures sheet still need to be recovered and integrated; do not replace them with placeholders. |
| Supplied weapons / medical / supply item art | 14-asset collection from prior uploads | Received in the conversation workspace; not yet committed to this repository or connected to inventory/pickup/combat systems. |
| Character sprite sheets / walk animations | Not found in the active repository tree | Still outstanding for playable character rendering and animation. |

## MAP 01 source audit

The uploaded archive is structurally valid. Its `scene_data.py` defines 39 entries: Zone A = 9, Zone B = 8, Zone C = 12, Zone D = 10. This disagrees with README/overview text that says 33 scenes. The integrated data follows the actual scene definitions and the 39 scene-card files.

The package is a room/zone layout schematic, drawn from rectangles, lines, text and tile coordinates. It is not a set of finished walkable environment textures. The app's MAP 01 browser uses the source-derived geometry and content, but collision, character navigation, zombie AI and scene-specific art rendering are not implemented by that integration.

## Preservation and integration notes

- Original user-generated artwork is not intentionally modified. Any runtime conversion must be kept as a derived copy, with source files retained.
- A file being present in an upload or archive does not mean it has been integrated into the game. Status distinguishes received, data-integrated, runtime-displayed and outstanding.
- Do not generate placeholder character or environment art to conceal missing production assets. Preserve the supplied originals and connect them when gameplay systems are ready.
