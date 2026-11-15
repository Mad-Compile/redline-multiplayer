# REDLINE

REDLINE is a native Godot 2D multiplayer survival game for Android. The visual direction is an atmospheric isometric world combining high-resolution illustrated environment art, selected HD pixel-art details, hand-detailed sprites and layered 2D lighting.

## Current map milestone

**Asymmetric Quarantine Arena — two-team wall-break / train-escape layout**

- Zombies and Survivors begin in separate territories.
- A segmented, collision-backed wall divides the arena.
- Zombies have three designated wall-weakening task stations in their territory.
- Survivors have generator, track-switch and train-fuel task stations.
- Survivor spawn markers and the train extraction area occupy the Survivor side.
- Team task areas, spawn markers and nine wall-segment collision bodies are created as actual Godot nodes.

This is a map foundation, not yet a playable match. Task progress, wall damage, combat, revive timing, player movement, online synchronization, final artwork and mobile controls still need their own implementations.

## Engine

- Godot **4.7.2-stable**
- GDScript and native Godot 2D rendering
- Mobile renderer (Android-first baseline)
- Isometric grid projection: 128 × 64 px cells
- Scene layers reserved for ground, environment, structures, actors, overhead elements and gameplay nodes

## Open the project

1. Install Godot 4.7.2-stable.
2. Import this repository's `project.godot`.
3. Run the project to inspect the active Asymmetric Quarantine Arena blockout.
4. Read [the current map specification](docs/ASYMMETRIC_ARENA.md) and [the asset handoff specification](docs/ART_HANDOFF.md).

The earlier Terminal 09 blockout is retained in the repository as inactive historical work; it is no longer the launch scene.

## Current status

- [x] Establish the native Godot project and Android export pipeline.
- [x] Establish the two-territory map footprint, central wall, task markers and team spawn markers.
- [x] Add wall-segment collision bodies and interaction areas for task stations.
- [ ] Implement team task progress and wall segment damage/state changes.
- [ ] Add player movement, mobile controls, combat and the 20-second downed/revive loop.
- [ ] Add train preparation and extraction flow.
- [ ] Import final environment artwork, animation, lighting, sound and ambience.
- [ ] Implement online multiplayer and offline AI teammates.
- [ ] Validate Android exports and test on actual devices.

A successful headless validation or APK export does not by itself mean the game has been playtested on an Android device.
