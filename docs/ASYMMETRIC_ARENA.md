# REDLINE — Asymmetric Quarantine Arena

## Match space and team territories

The asymmetric arena concept divides a quarantine yard into two territories separated by a reinforced wall:

- **The Dead (Zombies):** begin on the west side of the barrier.
- **Survivors:** begin on the east side, near the rail platform and escape train.

The early layout reference uses a 32 × 24 isometric grid, with the central barrier along grid column 16. These dimensions describe the early arena concept; the Python MAP 01 data package is a separate, larger 39-location layout.

## Zombie objective loop

Three zombie-side task locations are reserved for weakening the barrier:

1. Wall Node 01 affects wall segment 02.
2. Wall Node 02 affects wall segment 05.
3. Wall Node 03 affects wall segment 08.

The match-rule model supports team-locked objective work and destructible wall state. The complete in-world task interaction, synchronized wall presentation and breach effects still need to be connected to a playable match.

## Survivor objective loop

The survivor-side preparation concept includes:

1. Restore the generator.
2. Realign the tracks.
3. Fuel the train.

The complete train-preparation interaction sequence, boarding and escape condition remain to be implemented in gameplay.

## Barrier and spawn design

The barrier is divided into nine independently identified segments. Each segment begins with 100 health points and can track its broken state.

The design reserves three zombie spawn locations and three survivor spawn locations. Team-aware spawn selection and safety checks remain outstanding.

## Implementation status

The Python match-state module contains test-covered rules for match phases, wall damage, team-restricted objective progress, attack cooldowns, the survivor knockdown window and revival. Those rules are not yet a complete real-time match: movement, navigation, collision, player interaction, visual wall transitions, networking and the full escape flow still need implementation.

Final environment artwork must be integrated from the supplied production assets. Layout guides or procedural shapes are not substitutes for those assets.
