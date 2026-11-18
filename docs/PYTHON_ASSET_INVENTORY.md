# REDLINE Python migration — asset inventory

Inventory reconciled against the current Python branch and user uploads on 17 November 2026.

| Asset / source | Source / repository path | Status |
|---|---|---|
| Practice / Start Match / Settings button art | Original menu archive; recovered to `assets/menu/menu_buttons_recovered.zip` | Three intact original images decoded and verified by CI. The original archive remains unchanged. |
| Menu background WebP | Truncated final entry in `assets/menu/menu_art.zip` | Not recoverable from the committed archive. The menu still has a development background and displays a restoration warning. |
| REDLINE Theme Song.mp3 | Uploaded conversation file | Not committed to the repository; menu supports optional playback at `assets/audio/Redline Theme Song.mp3`. |
| REDLINE MAP 01 Python package | User upload `REDLINE_MAP01_Python.zip` (48 entries; ZIP integrity passes) | Source archive inspected. Contains a 4096×3200 overview, four zone images, 39 512×512 scene cards, renderer, and scene metadata. |
| MAP 01 room layout / connections / spawn points / objectives | `redline/gameplay/map_data.py` | **Integrated as source-derived data**: 39 locations, 128×100 tile layout, exits, loot tables, two spawn points, and eight survivor objectives. Automated validation added. |
| MAP 01 browser | `redline/gameplay/map_screen.py`; Practice menu action | **Integrated** as a scrollable, tappable schematic location browser. It displays the actual room coordinates and metadata. This is not a playable level. |
| Original MAP 01 overview and zone PNGs | Remain in the supplied ZIP | Preserved in the source upload, but not yet bundled as the in-game raster textures. The browser currently draws a schematic view from the source coordinates. |
| Original MAP 01 scene-card PNGs | `output/scenes/scene_*.png` inside supplied ZIP | 39 images received and inspected; not yet displayed in-game. |
| Gemini map package | Earlier staging branch under `maps/redline/` | Separate from the new Python MAP 01 upload. Its original atlas and structures sheet remain absent in the inspected branch; do not replace them with placeholders. |
| Uploaded weapons / medical / supply item art | 14-asset collection from the prior uploads | Received and packaged in the conversation workspace. Not yet committed to this branch or connected to inventory/pickup/combat systems. |
| Character sprite sheets / walk animations | Not found in the inspected repository branch trees | Still outstanding for playable character rendering and animation. |

## MAP 01 source audit

The uploaded archive is structurally valid. Its `scene_data.py` defines 39 entries: Zone A = 9, Zone B = 8, Zone C = 12, Zone D = 10. This disagrees with README/overview text that says 33 scenes. The Python integration follows the actual scene definitions and the 39 scene-card files.

The package is a **room/zone layout schematic**, drawn from rectangles, lines, text and tile coordinates. It is not a set of finished walkable environment textures. The app's Map 01 browser uses the source-derived geometry and content, but collision, character navigation, zombie AI and scene-specific art rendering are not implemented by that integration.

## Preservation and integration notes

- Original user/Gemini artwork is not intentionally modified. Re-encoded runtime versions must remain separate derived files, with the source files retained.
- A file being present in an upload or archive does not mean it has been integrated into the game. The statuses above distinguish received, data-integrated, runtime-displayed, and outstanding assets.
- Do not generate placeholder character/environment art to conceal missing production assets. Preserve the supplied originals and connect them when gameplay systems are ready.
