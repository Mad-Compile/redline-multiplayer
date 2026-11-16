# REDLINE Python migration — asset inventory

Inventory checked against the repository branches and uploaded files on 16 November 2026.

| Asset / source | Where it currently exists | Migration status |
|---|---|---|
| Menu background WebP | `assets/menu/menu_art.zip` on the asymmetric arena branch; preserved in this branch | Used by the Kivy menu loader |
| Practice button WebP | Same archive | Used by the Kivy menu loader |
| Start Match button WebP | Same archive | Used by the Kivy menu loader |
| Settings button WebP | Same archive | Used by the Kivy menu loader |
| REDLINE Theme Song.mp3 | Uploaded conversation file, approximately 4.6 MB | Available in workspace, not yet committed to repository; menu has optional playback support for `assets/audio/Redline Theme Song.mp3` |
| Gemini map scene and scripts | `staging/redline-map-ci` branch under `maps/redline/` | Source logic inspected; not yet fully ported |
| Gemini isometric atlas | Referenced by Gemini Tileset as `redline_iso_atlas.webp` | Missing from the inspected staging branch |
| Gemini structures sheet | Referenced by Gemini map scene as `redline_structures_sheet.webp` | Missing from the inspected staging branch |
| Character sprite sheets / walk animations | Not found in inspected repository branch trees | Not yet available to this migration branch |
| Other props / weapons / inventory art | Not found in inspected repository branch trees | Not yet available to this migration branch |

## Important integration notes

- The four menu images remain inside the original ZIP; the Python runtime decodes copies into its writable cache. The ZIP is not modified.
- The theme song has not been silently replaced with generated audio. It must be copied into the documented repository path before Android packaging can include it.
- The Gemini map code references artwork files that are not present in the inspected source branch. The map cannot be faithfully rendered from those references until the original image files are recovered. No procedural map art is being substituted.
- Assets absent from the inspected Git branches may still exist in the user's other AI sessions or local archives. They should be recovered and added, not regenerated.
