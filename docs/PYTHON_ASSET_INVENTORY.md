# REDLINE Python migration — asset inventory

Inventory checked against the repository branches and uploaded files on 16 November 2026.

| Asset / source | Where it currently exists | Migration status |
|---|---|---|
| Menu background WebP | Last entry in `assets/menu/menu_art.zip` | **Truncated and unrecoverable from the committed copy**; compressed stream is incomplete |
| Practice button WebP | Original archive; recovered to `assets/menu/menu_buttons_recovered.zip` | Intact; decoded and verified by CI test |
| Start Match button WebP | Original archive; recovered to `assets/menu/menu_buttons_recovered.zip` | Intact; decoded and verified by CI test |
| Settings button WebP | Original archive; recovered to `assets/menu/menu_buttons_recovered.zip` | Intact; decoded and verified by CI test |
| Original `menu_art.zip` | `assets/menu/menu_art.zip` | Preserved unchanged; it is 26,250 bytes and has no central directory; the fourth image's declared compressed stream extends beyond end-of-file |
| REDLINE Theme Song.mp3 | Uploaded conversation file, approximately 4.6 MB | Available in workspace, not yet committed to repository; menu has optional playback support for `assets/audio/Redline Theme Song.mp3` |
| Gemini map scene and scripts | `staging/redline-map-ci` branch under `maps/redline/` | Source logic inspected; not yet fully ported |
| Gemini isometric atlas | Referenced as `redline_iso_atlas.webp` | Missing from the inspected staging branch |
| Gemini structures sheet | Referenced as `redline_structures_sheet.webp` | Missing from the inspected staging branch |
| Character sprite sheets / walk animations | Not found in inspected repository branch trees | Not yet available to this migration branch |
| Other props / weapons / inventory art | Not found in inspected repository branch trees | Not yet available to this migration branch |

## Integration notes

- The three intact original menu button images were recovered byte-for-byte into a new valid ZIP. Their image payloads were not redrawn or replaced.
- The original ZIP remains untouched for provenance. Its background entry is truncated, so the current Python menu uses a plain development background and explicitly shows an artwork-restoration warning. This is not the finished menu.
- The theme song has not been replaced with generated audio. It must be copied into the documented repository path before Android packaging can include it.
- The Gemini map scene references artwork files absent from the inspected source branch. The map cannot be faithfully rendered from those references until the original images are recovered. No procedural map art is being substituted.
- Assets absent from the inspected Git branches may still exist in the user's other AI sessions or local archives. Recover the original files; do not regenerate them.
