import pytest

from redline.gameplay.match_state import (
    Phase, RedlineMatchState, SurvivorStatus, Team, WallSegment,
    ObjectiveStation, WallState,
)


def test_wall_sabotage_drops_armor_and_applies_bypass_damage():
    wall = WallSegment("north")
    before = wall.health
    wall.apply_sabotage(0.20, 350.0)
    assert wall.armor_resistance == pytest.approx(0.30)
    assert wall.health == pytest.approx(before - 350.0)


def test_phase_changes_only_when_zombie_enters_after_breach():
    match = RedlineMatchState(phase=Phase.BREACH)
    assert not match.zombie_entered_survivor_territory(False)
    assert match.phase == Phase.BREACH
    assert match.zombie_entered_survivor_territory(True)
    assert match.phase == Phase.HUNT


def test_attack_cooldown_and_knockdown_window():
    match = RedlineMatchState()
    match.register_survivor(7)
    assert match.try_zombie_attack(2, 7)
    assert match.survivors[7].status == SurvivorStatus.KNOCKED_DOWN
    assert not match.try_zombie_attack(2, 7)
    match.tick(2.5)
    assert match.can_zombie_attack(2)


def test_revive_completes_before_absolute_deadline():
    match = RedlineMatchState()
    match.register_survivor(7)
    match.register_survivor(8)
    assert match.try_zombie_attack(2, 7)
    assert match.begin_revive(8, 7)
    match.tick(3.5)
    assert match.survivors[7].status == SurvivorStatus.ACTIVE


def test_revive_does_not_pause_twenty_second_deadline():
    match = RedlineMatchState()
    match.register_survivor(7)
    match.register_survivor(8)
    assert match.try_zombie_attack(2, 7)
    assert match.begin_revive(8, 7)
    match.tick(20.0)
    assert match.survivors[7].status == SurvivorStatus.ELIMINATED


def test_objective_requires_correct_team_and_completes_once():
    station = ObjectiveStation("generator", Team.ZOMBIES, 8.0, "north")
    assert not station.advance(8.0, Team.SURVIVORS)
    assert station.advance(8.0, Team.ZOMBIES)
    assert station.completed
    assert not station.advance(1.0, Team.ZOMBIES)
