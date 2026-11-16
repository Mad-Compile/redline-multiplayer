"""Authoritative, engine-independent REDLINE match rules.

Values and phase transitions are ported from the supplied Gemini map module.
This module intentionally contains no substitute map art or fake actors.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict, Optional


class Team(str, Enum):
    SURVIVORS = "survivors"
    ZOMBIES = "zombies"


class Phase(IntEnum):
    PREPARATION = 0
    BREACH = 1
    HUNT = 2


class WallState(IntEnum):
    INTACT = 0
    DAMAGED = 1
    BREACHED = 2


class SurvivorStatus(IntEnum):
    ACTIVE = 0
    KNOCKED_DOWN = 1
    ELIMINATED = 2


@dataclass
class WallSegment:
    segment_id: str
    max_health: float = 1200.0
    health: float = 1200.0
    armor_resistance: float = 0.50
    damaged_threshold_ratio: float = 0.60

    @property
    def state(self) -> WallState:
        if self.health <= 0:
            return WallState.BREACHED
        if self.health / max(self.max_health, 1.0) <= self.damaged_threshold_ratio:
            return WallState.DAMAGED
        return WallState.INTACT

    def apply_damage(self, raw_damage: float, bypass_armor: bool = False) -> float:
        if raw_damage <= 0 or self.state == WallState.BREACHED:
            return 0.0
        mitigation = 0.0 if bypass_armor else self.armor_resistance
        applied = min(self.health, raw_damage * (1.0 - mitigation))
        self.health = max(0.0, self.health - applied)
        return applied

    def apply_sabotage(self, armor_drop: float, structural_damage: float) -> float:
        if self.state == WallState.BREACHED:
            return 0.0
        self.armor_resistance = min(0.9, max(0.0, self.armor_resistance - max(0.0, armor_drop)))
        # The source module applies sabotage structural damage with armor bypass.
        return self.apply_damage(structural_damage, bypass_armor=True)


@dataclass
class ObjectiveStation:
    station_id: str
    team: Team
    required_work_seconds: float
    target_wall_segment: Optional[str] = None
    sabotage_armor_reduction: float = 0.20
    sabotage_structural_damage: float = 350.0
    work_seconds: float = 0.0
    completed: bool = False

    def advance(self, delta_seconds: float, interacting_team: Team) -> bool:
        if self.completed or interacting_team != self.team or delta_seconds <= 0:
            return False
        self.work_seconds = min(self.required_work_seconds, self.work_seconds + delta_seconds)
        if self.work_seconds >= self.required_work_seconds:
            self.completed = True
            return True
        return False


@dataclass
class SurvivorState:
    peer_id: int
    status: SurvivorStatus = SurvivorStatus.ACTIVE
    remaining_revive_time: float = 20.0
    revive_progress: float = 0.0
    rescuer_peer_id: Optional[int] = None


@dataclass
class RedlineMatchState:
    """Single authoritative match-state model; networking transport is separate."""

    attack_cooldown_seconds: float = 2.5
    knockdown_window_seconds: float = 20.0
    revive_channel_seconds: float = 3.5
    phase: Phase = Phase.PREPARATION
    wall_segments: Dict[str, WallSegment] = field(default_factory=dict)
    zombie_tasks: Dict[str, ObjectiveStation] = field(default_factory=dict)
    survivor_tasks: Dict[str, ObjectiveStation] = field(default_factory=dict)
    survivors: Dict[int, SurvivorState] = field(default_factory=dict)
    zombie_cooldowns: Dict[int, float] = field(default_factory=dict)
    train_escape_ready: bool = False

    def complete_zombie_task(self, station_id: str) -> bool:
        station = self.zombie_tasks[station_id]
        if not station.completed:
            return False
        wall = self.wall_segments.get(station.target_wall_segment or "")
        if wall is None:
            return False
        before = wall.state
        wall.apply_sabotage(
            station.sabotage_armor_reduction,
            station.sabotage_structural_damage,
        )
        if wall.state == WallState.BREACHED and before != WallState.BREACHED:
            if self.phase == Phase.PREPARATION:
                self.phase = Phase.BREACH
        return True

    def complete_survivor_task(self, station_id: str) -> bool:
        station = self.survivor_tasks[station_id]
        if not station.completed:
            return False
        self.train_escape_ready = bool(self.survivor_tasks) and all(
            item.completed for item in self.survivor_tasks.values()
        )
        return True

    def zombie_entered_survivor_territory(self, is_zombie: bool) -> bool:
        if not is_zombie or self.phase != Phase.BREACH:
            return False
        self.phase = Phase.HUNT
        return True

    def register_survivor(self, peer_id: int) -> None:
        self.survivors[peer_id] = SurvivorState(
            peer_id=peer_id,
            remaining_revive_time=self.knockdown_window_seconds,
        )

    def can_zombie_attack(self, zombie_peer_id: int) -> bool:
        return self.zombie_cooldowns.get(zombie_peer_id, 0.0) <= 0.0

    def try_zombie_attack(self, zombie_peer_id: int, survivor_peer_id: int) -> bool:
        if not self.can_zombie_attack(zombie_peer_id):
            return False
        survivor = self.survivors.get(survivor_peer_id)
        if survivor is None:
            self.register_survivor(survivor_peer_id)
            survivor = self.survivors[survivor_peer_id]
        if survivor.status != SurvivorStatus.ACTIVE:
            return False
        self.zombie_cooldowns[zombie_peer_id] = self.attack_cooldown_seconds
        survivor.status = SurvivorStatus.KNOCKED_DOWN
        survivor.remaining_revive_time = self.knockdown_window_seconds
        survivor.revive_progress = 0.0
        survivor.rescuer_peer_id = None
        return True

    def begin_revive(self, rescuer_peer_id: int, downed_peer_id: int) -> bool:
        if rescuer_peer_id == downed_peer_id:
            return False
        rescuer = self.survivors.get(rescuer_peer_id)
        downed = self.survivors.get(downed_peer_id)
        if rescuer is None or downed is None:
            return False
        if rescuer.status != SurvivorStatus.ACTIVE:
            return False
        if downed.status != SurvivorStatus.KNOCKED_DOWN or downed.remaining_revive_time <= 0:
            return False
        downed.rescuer_peer_id = rescuer_peer_id
        return True

    def cancel_revive(self, rescuer_peer_id: int, downed_peer_id: int) -> None:
        downed = self.survivors.get(downed_peer_id)
        if downed and downed.rescuer_peer_id == rescuer_peer_id:
            downed.rescuer_peer_id = None
            downed.revive_progress = 0.0

    def tick(self, delta_seconds: float) -> None:
        if delta_seconds <= 0:
            return
        for zombie_id in list(self.zombie_cooldowns):
            remaining = max(0.0, self.zombie_cooldowns[zombie_id] - delta_seconds)
            if remaining:
                self.zombie_cooldowns[zombie_id] = remaining
            else:
                del self.zombie_cooldowns[zombie_id]

        for survivor in self.survivors.values():
            if survivor.status != SurvivorStatus.KNOCKED_DOWN:
                continue
            # The 20-second deadline runs even while a revive is in progress.
            survivor.remaining_revive_time = max(
                0.0, survivor.remaining_revive_time - delta_seconds
            )
            if survivor.remaining_revive_time <= 0.0:
                survivor.status = SurvivorStatus.ELIMINATED
                survivor.rescuer_peer_id = None
                survivor.revive_progress = 0.0
                continue
            if survivor.rescuer_peer_id is not None:
                survivor.revive_progress += delta_seconds
                if survivor.revive_progress >= self.revive_channel_seconds:
                    survivor.status = SurvivorStatus.ACTIVE
                    survivor.revive_progress = 0.0
                    survivor.rescuer_peer_id = None
