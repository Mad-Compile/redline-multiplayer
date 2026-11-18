# Terminal 09 — Quarantine Rail Yard

## Purpose

Terminal 09 is an early REDLINE map concept built around the two-team survival loop:

- Survivors begin inside a defensible maintenance compound.
- The opposing team approaches from the infected perimeter and tries to breach the compound.
- Survivors search for equipment, complete repair objectives and prepare the locomotive.
- Survivors who reach the departing train escape; the opposing team wins by eliminating the survivors before extraction.

Exact player counts, match duration, round balance, objective timing and escape eligibility require playtesting and are not locked by this blueprint.

## Spatial specification

- Isometric grid: **36 × 24 cells**.
- Tile footprint: **128 × 64 source pixels** (2:1 diamond).
- Approximate projected footprint: **3,840 × 1,920 px**, before overhangs and decorative props.
- Grid coordinate projection: `screen_x = origin_x + (x - y) × 64`; `screen_y = origin_y + (x + y) × 32`.

This is an engine-independent layout and art specification. The current Python MAP 01 browser uses a different, user-supplied 39-location layout.

## Map sectors

| Sector | Role |
|---|---|
| Secure maintenance compound | Survivor start, initial protection, storage and medical staging |
| Generator and service shed | Power restoration objective; narrow interior routes |
| Central switching yard | Main contested traversal space, cover, rail obstacles and route choices |
| North freight approach | Long, exposed infected approach with the freight-gate breach |
| West drainage route | Tighter, lower-visibility approach with the drain breach |
| Passenger platform | Locomotive, fuel objective and final extraction approach |

## First-pass map points

### Survivor start

A survivor start location inside the maintenance compound. Player spawn selection and team balancing remain separate match-system responsibilities.

### Infected entries

Three perimeter entry locations (north, west and east). These are layout points, not a final decision about how many player-controlled or AI-controlled zombies spawn.

### Breach points

1. North freight gate.
2. West drainage opening.
3. East platform tunnel.

Each breach point needs its own collision, interaction state, sound, animation and network replication when the playable level is implemented.

### Survivor objectives

1. Restore the generator in the service shed.
2. Realign the track switch in the central yard.
3. Refuel the locomotive near the platform.

The objectives encourage movement across the map and make the escape route legible. Their order and completion requirements need playtesting.

### Extraction

The train is the map-specific escape vehicle. Its platform and interaction location are reserved at the eastern end. Train art, animation, doors, boarding checks and departure logic remain outstanding.

## Visual and rendering plan

The final map should be assembled from separate, texture-backed layers with deliberate depth ordering:

1. Ground and ground-detail art.
2. Roads, rail infrastructure and platform surfaces.
3. Architecture and large structures.
4. Props and set dressing.
5. Actors.
6. Overhead art and foreground occluders.
7. Lighting and atmosphere.
8. Gameplay interaction zones, collision and navigation data.

The environment can mix detailed painted/high-resolution textures with selected HD pixel-art elements. Pixel treatment is an art choice per asset, not a blanket filter applied to the whole world.

Large buildings, trees, machinery, vehicles and foreground pieces should remain independent assets so their pivots, depth ordering, collision and occlusion can be tuned individually.

## Implementation sequence

1. Confirm map footprint and sector flow using the layout data.
2. Reconcile the environment asset package and record each asset's source.
3. Integrate painted ground and service-road layers.
4. Add buildings, walls, rail geometry, fences and platforms.
5. Add collision and navigation after walkable geometry is stable.
6. Add prop dressing, interaction points, loot locations, lights and ambience.
7. Test sight lines, escape routes, breach balance, readability and mobile performance.

## Environment asset families

- **Ground:** worn concrete, ballast/gravel, cracked asphalt, drainage mud, wet patches, grass margins, oil stains and safety markings.
- **Rail:** straight, curved, junction, switch, buffer stop, crossing, sleepers, rail-bed transitions and platform edges.
- **Structural:** concrete walls, chain-link fences, gates, retaining walls, stairs, ramps, door frames, roof edges and canopy pieces.
- **Industrial:** generator shed modules, cable trays, transformers, fuel storage, loading docks, signal cabinets and trackside electrical boxes.
- **Platform:** platform top/edge/corner pieces, canopy supports, benches, lamps, signs, ticket booth and train boarding edge.
- **Set dressing:** freight containers, pallets, crates, barrels, sandbags, road barriers, cable drums, abandoned luggage, broken signage and litter.
- **Outbreak storytelling:** quarantine tape, temporary checkpoints, medical waste bins, emergency lights, evacuation notices, abandoned response equipment and restrained blood traces.

Every tile family needs matching edge/corner transitions. Large structures should remain separate assets with explicit pivots, depth ordering, collision and occlusion rather than being flattened into the ground atlas.

## Completion gates

The map is not complete until the supplied production environment artwork is connected to the game, walkable geometry and collision are implemented, objective and breach interactions work, and the complete extraction route has been tested in a running Android build. Layout drawings and blockout guides are not finished art or a playable level.
