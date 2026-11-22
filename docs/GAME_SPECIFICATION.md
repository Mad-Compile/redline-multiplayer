# REDLINE — Game Specification

**Project:** REDLINE  
**Map:** MAP 01 — Train Escape  
**Platform:** Android-first  
**Runtime:** Python 3.11+ and Kivy 2.3.1  
**Camera direction:** First-person 2.5D (ray-cast view over a 2D collision grid)

This document records the intended game scope and separates the current prototype from features that still require implementation.

## 1. Game overview

REDLINE is a zombie-survival game set around an abandoned rail facility. Survivors explore the location, complete preparation and repair objectives, and attempt to escape by train. The opposing Dead (zombie) side pressures survivor territory and tries to stop the escape.

The current project is an Android-first prototype. A successful APK build means the app packaged; it does not by itself prove that every gameplay system is complete or device-tested.

## 2. Platform and technology

- Android phones in landscape orientation.
- Python 3.11+.
- Kivy 2.3.1 for rendering, touch input and application lifecycle.
- Pillow for image decoding.
- Buildozer / python-for-android for APK packaging.
- GitHub Actions for automated validation and Android debug builds.

Keep the existing Kivy project unless a measured technical limitation justifies a migration.

## 3. Camera and world

- First-person perspective using a 2.5D ray-cast renderer.
- A 2D tile grid is the source of truth for walkable floor and solid walls.
- MAP 01 is derived from the authored 39-location scene data.
- Rooms have enclosed boundaries and walkable interiors.
- Connected locations are joined by corridors and doorway openings.
- The overhead map artwork is a layout/reference image, not the gameplay view.
- The map may also be shown as an optional minimap/reference panel.
- The current generated room layout is a playable foundation; it is not yet a hand-authored, faithful interior recreation of every building shown in the artwork.

## 4. Player controls

### Required mobile controls

- Left-side virtual joystick: move forward/back and strafe.
- Right-side touch drag: turn/look horizontally.
- Sprint control: increase movement speed while held.
- Interact control: interact with nearby doors, objects and objectives.
- Pause control: open the pause/settings overlay.

### Movement behaviour

- Walk and sprint movement.
- Smooth turning and configurable look sensitivity.
- Collision against solid walls and map boundaries.
- No movement through closed walls.
- First-person movement bob while walking/running.
- Idle camera settles when the player stops.

## 5. World interaction and animation

Target features:

- Doorway transitions and animated doors.
- Environmental ambience such as lights, dust and subtle particles.
- Footstep audio and location ambience.
- Non-graphic zombie idle, patrol and chase movement.
- Interactable objective props with clear feedback.
- Readable location names and objective markers.

Only features actually implemented and tested should be marked complete in the implementation tracker.

## 6. Map 01 — Train Escape

The supplied scene data defines 39 named locations across the map. The world should preserve those names and their spatial relationships.

Target exploration requirements:

- Spawn the player in the intended survivor starting location.
- Make all authored locations reachable through the connected world.
- Give each location a recognizable identity and suitable interior/exterior layout.
- Add appropriate doors, obstacles, props and objective interaction points.
- Keep collision and navigation data aligned with the visible geometry.

The current grid generator creates basic room footprints and connecting corridors from the source scene coordinates. Detailed room-by-room layouts, distinctive production art and full interaction dressing remain future work.

## 7. Core game loop

### Survivor side

1. Explore the facility.
2. Find and complete preparation/repair objectives.
3. Restore the systems needed for the train escape.
4. Reach the passenger platform.
5. Board the train and complete extraction.

### Dead (zombie) side

1. Begin in the opposing territory.
2. Pressure the survivor perimeter.
3. Complete the breach progression objectives.
4. Enter survivor territory after the breach.
5. Stop survivors from completing the escape.

### Match phases

- Preparation.
- Breach.
- Hunt.
- Escape / match result.

The existing engine-independent match rules cover preparation/breach/hunt progression, wall damage, team-locked objectives, attack cooldowns, knockdown and revival. Full in-world presentation and a complete match session are separate implementation tasks.

## 8. UI and accessibility

- Main menu with Practice and Start Match.
- Settings entry point.
- Gameplay HUD for location, objectives and player state.
- Pause/resume flow.
- Touch targets sized for phone screens.
- Adjustable look sensitivity and audio levels.
- Clear feedback for blocked movement and unavailable interactions.

## 9. Multiplayer target

The long-term target is an online multiplayer match with survivor and Dead teams. This requires an authoritative session/server design, player synchronization, reconnection handling and server-validated match state. Do not describe multiplayer as complete until real devices can join and complete a synchronized match.

## 10. Quality gates before calling a build playable

### Automated checks

- Map data loads and contains all 39 authored locations.
- Every authored room is reachable from the survivor spawn.
- Player movement changes position on walkable tiles.
- Turning changes the camera/ray direction.
- Collision prevents crossing walls and map boundaries.
- Ray casting returns valid wall hits.
- App navigation and Kivy screen startup pass.
- Android APK build completes successfully.

### Manual Android checks

- Install and launch the APK on a real Android phone.
- Enter Practice and reach the first-person exploration screen.
- Move in all directions and turn smoothly.
- Verify that walls block movement and door openings allow passage.
- Visit multiple named rooms and confirm the location indicator.
- Test sprint, interact, pause and resume.
- Check touch controls, frame rate, screen scaling and app lifecycle.
- Confirm that no blank/white gameplay screen or crash occurs.

A passing unit-test suite is necessary but not sufficient: manual on-device playtesting is still required.

## 11. Implementation status

| System | Current status |
|---|---|
| Android/Kivy application and menu | Implemented |
| Settings persistence | Implemented |
| Source-derived 39-location map data | Implemented |
| First-person 2.5D ray-cast foundation | Implemented |
| Generated room/corridor grid | Implemented |
| Basic movement and wall collision | Implemented |
| Touch joystick and swipe-look foundation | Implemented |
| Automated world/connectivity/movement/raycast tests | Implemented |
| Full detailed interiors matching the supplied artwork | Planned |
| Production wall/floor/prop textures | Planned |
| Complete animated doors and object interactions | Planned |
| Full zombie AI and polished animation/audio | Planned |
| Complete objective-to-train extraction gameplay | In progress / not complete |
| Authoritative online multiplayer | Planned |
| Full real-device gameplay QA | Required |

## 12. Definition of playable

A build may be called a **first-person exploration prototype** after it passes the automated checks and the manual Android movement, turning, doorway, collision and map-loading checks.

A build may be called a **complete REDLINE match** only after both teams, objectives, zombie behaviour, extraction, match results and real multiplayer synchronization work end-to-end.
