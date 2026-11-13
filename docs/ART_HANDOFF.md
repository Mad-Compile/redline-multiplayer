# REDLINE — Asset handoff specification

This is the shared scale and export contract for the first asset batch. The world is isometric, but individual assets do **not** all need to be pixelated. Use polished HD illustration/painting where appropriate and controlled HD pixel-art detail where it suits the asset. Avoid a forced 16×16 or 32×32 retro look.

## Item artwork

### Canvas sizes

Use these source canvases:

| Asset type | Canvas |
|---|---:|
| Medicine, bandages, pills, small pickups, keys | **256 × 256 px** |
| Pistols, grenades, compact tools | **256 × 256 px** |
| Rifles, shotguns, long melee weapons | **512 × 256 px** |
| Backpacks, med bags, supply crates, larger gear | **512 × 512 px** |
| Optional inventory-only icon | **128 × 128 px** |

The canvas is the source image size, not the on-screen size. The game will scale items for the world and for the six-slot hotbar.

### Export rules

- Format: PNG, 8-bit RGBA, transparent background.
- Colour: sRGB.
- One item per file; do not combine unrelated items into a sheet.
- Keep the complete silhouette inside the canvas with about **8–12% transparent padding**.
- Make the item occupy roughly **75–85%** of the available canvas.
- No background, floor, tile, border, UI frame, text, watermark, or fake drop shadow.
- Keep the light direction and material treatment consistent across an item set.
- Avoid baked ground shadows; the game will add contact shadows and dynamic lighting.
- Give the object a clear, readable silhouette at small size. Tiny details should not be the only way to distinguish two items.

### Isometric camera angle

Draw pickups as though viewed from a **three-quarter overhead/isometric camera**: show the top surface and enough side depth to make the object feel grounded in the world. Do not draw everything as a flat side-view icon.

For long items such as rifles, use the 512 × 256 canvas and align the item's long axis consistently with one of the isometric ground directions. Use the same angle across the weapon family.

### Item naming

Use lowercase snake case and stable IDs:

- `item_medkit.png`
- `item_bandage.png`
- `item_painkillers.png`
- `weapon_pistol_01.png`
- `weapon_rifle_01.png`
- `ammo_9mm.png`
- `gear_backpack_01.png`

If an inventory icon is drawn separately, append `_icon` before the extension, for example `item_medkit_icon.png`.

## Copyable prompt for an individual item

Replace the bracketed words for each asset:

> Create a production-ready 2D game asset of **[ITEM NAME]** for REDLINE, a premium isometric multiplayer survival game. Show the object from a three-quarter overhead/isometric camera angle, with a clear silhouette and believable volume. Use polished high-resolution illustrated rendering with carefully controlled HD pixel-art detailing only where it improves the material; do not force a low-resolution retro pixel style. Keep the object's proportions and material details realistic and readable at small mobile-game sizes. Isolate exactly one object on a fully transparent background. No floor, no scene, no cast shadow, no text, no labels, no border, no UI, no watermark. Use consistent neutral studio lighting from the upper-left. Export as a **[256×256 / 512×256 / 512×512] px PNG with transparent RGBA background**, centered with 8–12% clear padding.

## Character artwork — separate from item canvases

Do not use the item canvas dimensions for characters. Character animation needs a fixed frame grid:

- Recommended source frame: **256 × 256 px per frame**.
- One consistent frame size for every direction and animation.
- Transparent PNG sprite sheets.
- Feet/ground-contact anchor at the same position in every frame (approximately x=128, y=226).
- Keep the full silhouette inside each frame; no cropping between frames.
- Use a consistent camera angle and body proportions across all characters.

For the first character pass, begin with a clean still/reference pose and a small directional test. We will lock the complete 8-direction walk/idle/attack sheet layout after checking one sample in the game, so you do not waste time drawing a large sheet at the wrong angle.

## Drop location

Put delivered source files under:

- `assets/items/`
- `assets/items/icons/` (if separate inventory icons are supplied)
- `assets/characters/`

Keep original source files. Do not flatten several unrelated items into one image.
