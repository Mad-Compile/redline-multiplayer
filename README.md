# REDLINE

REDLINE is a native Godot 2D multiplayer survival game for Android. The visual direction is an isometric world that mixes high-resolution illustrated environment art, selected HD pixel-art details, hand-detailed sprites, and smooth real-time 2D lighting. The whole world is **not** required to be pixelated.

## Current milestone

**Map foundation: Terminal 09 — Quarantine Rail Yard**

This branch establishes the first map's isometric grid, scene layers, named gameplay markers, and a developer blockout overlay. It is an early map foundation, not a playable match and not finished environment art.

The first map is a derelict rail terminal. Survivors begin inside a fortified maintenance compound; the opposing team approaches from perimeter routes and can attempt three breach points. Survivors work to restore the generator, realign the track switch, and fuel the locomotive before extraction.

## Engine

- Godot **4.7.2-stable**
- GDScript
- Godot 2D renderer: Mobile (Android-first baseline)
- Isometric TileSet grid: 128 × 64 px cells
- Separate ground, ground-detail, world-object, actor, overhead, lighting, and gameplay layers

The Mobile renderer is the starting configuration, not a claim of tested performance on every Android device. A Compatibility-renderer pass and device testing remain necessary.

## Open the project

1. Install Godot 4.7.2-stable.
2. Import this repository's `project.godot`.
3. Run the project to inspect the Terminal 09 map blockout.
4. Read [the map blueprint](docs/MAP_BLUEPRINT.md) and [the asset handoff specification](docs/ART_HANDOFF.md).

## Current status

- [x] Inspect the new repository and confirm the starting point.
- [x] Establish the native Godot project and isometric map foundation.
- [x] Define the first map's zones, spawn markers, breach points, and objectives.
- [ ] Import final environment artwork and build the finished tile/prop atlases.
- [ ] Add collision, occlusion, navigation, and interactive breach/objective logic.
- [ ] Add player movement, mobile controls, match flow, and multiplayer synchronisation.
- [ ] Validate Android exports and test on actual devices.

No APK or playable gameplay milestone is claimed by this commit.
