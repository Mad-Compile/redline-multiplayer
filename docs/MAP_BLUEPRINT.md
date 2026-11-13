# Terminal 09 — Quarantine Rail Yard

## Purpose

Terminal 09 is the first REDLINE map. It is designed around the current two-team loop:

- Survivors begin inside a defensible maintenance compound.
- The opposing team approaches from the infected perimeter and tries to breach the compound.
- Survivors search for randomly selected equipment, complete repair objectives, and prepare the locomotive.
- Survivors who reach the departing train escape; the opposing team wins by eliminating the survivors before extraction.

This document defines a first layout pass. Exact player counts, match duration, round balance, objective timing, and escape eligibility are not locked here.

## Spatial specification

- Isometric grid: **36 × 24 cells**.
- Tile footprint: **128 × 64 source pixels** (2:1 diamond).
- Approximate projected footprint: **3,840 × 1,920 px**, before overhangs and decorative props.
- Grid coordinate projection: `screen_x = origin_x + (x - y) × 64`; `screen_y = origin_y + (x + y) × 32`.
- The game remains a native 2D project. The isometric depth comes from the TileSet layout, Y-sorting, layered sprites, occlusion, lighting, and art—not from a web or 3D-in-a-browser implementation.

## Map sectors

| Sector | Role |
|---|---|
| Secure maintenance compound | Survivor start, initial protection, storage, revive/medical staging |
| Generator and service shed | Power restoration objective; narrow interior routes |
| Central switching yard | Main contested traversal space, cover, rail obstacles, route choices |
| North freight approach | A long, exposed infected approach with the freight-gate breach |
| West drainage route | A tighter, lower-visibility approach with the drain breach |
| Passenger platform | Locomotive, fuel objective, final extraction approach |

## First-pass map points

### Survivor start

One survivor start marker inside the maintenance compound. Player spawn selection and team balancing remain a separate match-system concern.

### Infected entries

Three perimeter entry markers (north, west, east). These are map data points, not a final decision about how many player-controlled zombies or AI-controlled zombies spawn.

### Breach points

1. North freight gate.
2. West drainage opening.
3. East platform tunnel.

Each breach point will eventually be a distinct gameplay scene with its own collision, interaction state, sound, animation, and replication. The current markers only reserve their positions.

### Survivor objectives

1. Restore the generator in the service shed.
2. Realign the track switch in the central yard.
3. Refuel the locomotive near the platform.

The three objectives create movement across the map and make the escape route legible. Objective order and completion requirements will be tuned during playtesting.

### Extraction

The train is the map-specific escape vehicle. Its platform and interaction marker are reserved at the eastern end of the map. Train art, animation, doors, boarding checks, and departure logic are not implemented yet.

## Layer and rendering plan

The Godot scene is separated into:

1. Ground TileMapLayer.
2. Ground-detail TileMapLayer.
3. Y-sorted world structures.
4. Y-sorted props.
5. Y-sorted actors.
6. Overhead art (roof pieces, signs, canopies, foreground occluders).
7. Lighting.
8. Gameplay markers and invisible gameplay geometry.

The environment can mix detailed painted/high-resolution textures with selected HD pixel-art elements. Pixel treatment is an art choice per asset, not a blanket filter applied to the whole world.

Ground tiles will use the isometric TileSet. Larger buildings, trees, machinery, vehicles, and foreground pieces should be independent scene/sprite assets so their pivots, Y-sort origin, collision shapes, and occluders can be tuned individually.

## Implementation sequence

1. Confirm map footprint and sector flow using the included debug blockout.
2. Establish a coherent environment asset pack and record each asset's licence.
3. Paint the ground and service-road layers.
4. Add buildings, walls, rail geometry, fences, platforms, and collision.
5. Add occlusion and navigation after the walkable geometry is fixed.
6. Add prop dressing, interaction points, randomized loot sockets, lights, weather, and ambience.
7. Test sight lines, escape routes, breach balance, readability, and mobile frame time.

The current scene intentionally contains no finished placeholder artwork. The coloured overlay is only a layout/debug aid.
