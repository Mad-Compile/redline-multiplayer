# REDLINE — Asymmetric Quarantine Arena

## Match space

The active map is a 32 × 24 isometric grid using 128 × 64 px tile footprints. The central wall follows grid column 16 and divides the level into two distinct team territories:

- **Zombies / The Dead:** west side of the barrier.
- **Survivors:** east side of the barrier, including the rail platform and extraction train.

The map is drawn with deterministic blockout geometry so its route layout and gameplay points can be reviewed before final painted environment assets are integrated. It is not final environment art.

## Core route and objectives

### Zombie territory

Three task stations reserve the zombie-side wall-weakening objective loop. Each station is an Area2D with a stable task ID, team metadata and a link to the wall segment it affects:

1. Wall Node 01 → wall segment 02.
2. Wall Node 02 → wall segment 05.
3. Wall Node 03 → wall segment 08.

These links are map metadata only. Completing a task does not yet damage the wall; task progress, authority checks, wall health and destruction effects remain to be implemented in the match system.

### Survivor territory

Three task stations reserve the train-preparation loop:

1. Restore Generator.
2. Realign Tracks.
3. Fuel the Train.

These are native Area2D interaction volumes with team and task metadata. The map does not yet implement their progress or the final extraction condition.

## Barrier

The dividing wall has nine separate StaticBody2D collision segments. Every segment has a stable ID, 100-point starting health metadata and a broken-state metadata flag. The visual blockout draws the barrier as segmented reinforced concrete.

The metadata is an interface for the future wall-state system, not a claim that wall damage or segment destruction is currently playable.

## Team spawns

Six Marker2D spawn markers are provided: three distributed across the zombie territory and three across the survivor territory. Each marker has a stable ID, team metadata and a team-specific group.

The matchmaker will later select valid spawn markers based on team size and safety checks. No automatic balancing or spawn selection is implemented in this map foundation.

## Scene structure

- `scenes/maps/asymmetric_arena/asymmetric_arena_map.tscn`: active arena scene.
- `scripts/maps/asymmetric_arena_map.gd`: procedural ground, blockout structures, railway, wall drawing and gameplay-node construction.
- `scenes/main/main.tscn`: launch scene and full-map camera.
- `Gameplay/WallSegments`: nine collision-backed wall segments.
- `Gameplay/TaskStations`: six interaction areas.
- `Gameplay/SpawnPoints`: six team spawn markers.

The earlier Terminal 09 scene and blueprint remain in the repository but are not instantiated by the launch scene.

## Next integration gates

1. Add task-progress handlers and host-authoritative wall-segment health.
2. Break wall collision and visual state together when a segment reaches zero health.
3. Implement Survivor progress persistence across the generator, switch and fuel tasks.
4. Add player navigation/collision, interaction prompts and team-safe spawn validation.
5. Replace blockout shapes with the supplied REDLINE artwork and build proper occlusion/light layers.
6. Run Godot import and launch validation in GitHub Actions, then export and install the Android APK for device testing.
