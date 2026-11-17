from redline.gameplay.map_data import load_map_layout


def test_map_layout_has_all_39_authored_locations():
    layout = load_map_layout()
    assert len(layout["scenes"]) == 39
    assert {scene["id"] for scene in layout["scenes"]} == {
        "dead_end", "iron_yard", "rust_factory", "scrap_depot", "power_ruins",
        "shattered_warehouse", "corruption_lab", "breach_control", "waste_grounds",
        "north_breach", "red_barrier", "east_breach", "dead_gate", "watch_post",
        "ctrl_node", "south_breach", "breach_entry", "security_hq",
        "residential_block", "watchtower", "safe_haven", "med_bay", "supply_hub",
        "tool_shed", "generator_room", "central_courtyard", "fuel_depot",
        "communication_room", "parking_lot", "engine_repair", "fuel_station",
        "electrical_bay", "terminal_zero", "locomotive_bay", "passenger_platform",
        "signal_control", "track_control", "maintenance_depot", "departure_track",
    }


def test_map_spawn_points_match_supplied_map():
    layout = load_map_layout()
    assert layout["spawn_points"]["zombie"]["scene"] == "dead_end"
    assert layout["spawn_points"]["survivor"]["scene"] == "safe_haven"


def test_every_authored_room_connection_resolves():
    layout = load_map_layout()
    ids = {scene["id"] for scene in layout["scenes"]}
    for scene in layout["scenes"]:
        for connection in scene.get("exits", []) + scene.get("connects", []):
            assert connection in ids, (scene["id"], connection)


def test_survivor_escape_objectives_match_supplied_sequence():
    layout = load_map_layout()
    assert [item["id"] for item in layout["objectives"]] == [
        "power_generator",
        "repair_engine",
        "fuel_train",
        "power_train",
        "set_signals",
        "set_tracks",
        "board_train",
        "escape_win_condition",
    ]
