extends Node2D
## REDLINE asymmetric team arena.
## This is a spatial/gameplay foundation: task stations and wall collision are real
## scene nodes, while match rules, damage replication, art and player controllers
## remain separate systems.

const GRID_SIZE := Vector2i(32, 24)
const HALF_TILE := Vector2(64.0, 32.0)
const GRID_ORIGIN := Vector2(1536.0, 0.0)
const WALL_GRID_X := 16.0
const WALL_SEGMENT_COUNT := 9
const WALL_THICKNESS := 28.0

const TASK_STATIONS: Array[Dictionary] = [
	{
		"id": "wall_node_01",
		"label": "WALL NODE 01",
		"team": "zombies",
		"cell": Vector2i(5, 5),
		"kind": "weaken_wall",
		"wall_segment": "wall_segment_02",
	},
	{
		"id": "wall_node_02",
		"label": "WALL NODE 02",
		"team": "zombies",
		"cell": Vector2i(10, 12),
		"kind": "weaken_wall",
		"wall_segment": "wall_segment_05",
	},
	{
		"id": "wall_node_03",
		"label": "WALL NODE 03",
		"team": "zombies",
		"cell": Vector2i(5, 19),
		"kind": "weaken_wall",
		"wall_segment": "wall_segment_08",
	},
	{
		"id": "generator_restore",
		"label": "RESTORE GENERATOR",
		"team": "survivors",
		"cell": Vector2i(21, 5),
		"kind": "repair_generator",
	},
	{
		"id": "track_switch",
		"label": "REALIGN TRACKS",
		"team": "survivors",
		"cell": Vector2i(26, 11),
		"kind": "repair_switch",
	},
	{
		"id": "train_fuel",
		"label": "FUEL THE TRAIN",
		"team": "survivors",
		"cell": Vector2i(24, 19),
		"kind": "fuel_train",
	},
]

const TEAM_SPAWNS: Array[Dictionary] = [
	{"id": "zombie_spawn_north", "team": "zombies", "cell": Vector2i(3, 3)},
	{"id": "zombie_spawn_centre", "team": "zombies", "cell": Vector2i(3, 12)},
	{"id": "zombie_spawn_south", "team": "zombies", "cell": Vector2i(3, 21)},
	{"id": "survivor_spawn_north", "team": "survivors", "cell": Vector2i(29, 3)},
	{"id": "survivor_spawn_centre", "team": "survivors", "cell": Vector2i(29, 12)},
	{"id": "survivor_spawn_south", "team": "survivors", "cell": Vector2i(29, 21)},
]

const TEAM_ZOMBIE := Color(0.83, 0.30, 0.24, 1.0)
const TEAM_SURVIVOR := Color(0.25, 0.73, 0.86, 1.0)


func _ready() -> void:
	_build_wall_collision()
	_build_task_areas()
	_build_spawn_markers()
	queue_redraw()


## Isometric cell coordinates to world-space tile centre.
func grid_to_world(cell: Vector2) -> Vector2:
	return GRID_ORIGIN + Vector2(
		(cell.x - cell.y) * HALF_TILE.x,
		(cell.x + cell.y) * HALF_TILE.y
	)


func _build_wall_collision() -> void:
	var wall_root := get_node_or_null("Gameplay/WallSegments") as Node2D
	if wall_root == null:
		push_warning("AsymmetricArena: Gameplay/WallSegments is missing.")
		return

	var segment_step: float = float(GRID_SIZE.y) / float(WALL_SEGMENT_COUNT)
	var axis := Vector2(-HALF_TILE.x, HALF_TILE.y).normalized()
	var segment_length: float = segment_step * Vector2(-HALF_TILE.x, HALF_TILE.y).length()

	for index in range(WALL_SEGMENT_COUNT):
		var centre_y: float = (float(index) + 0.5) * segment_step
		var segment_id := "wall_segment_%02d" % (index + 1)
		var body := StaticBody2D.new()
		body.name = "WallSegment_%02d" % (index + 1)
		body.position = grid_to_world(Vector2(WALL_GRID_X, centre_y))
		body.collision_layer = 1
		body.collision_mask = 1
		body.add_to_group("breakable_wall_segment")
		body.set_meta("wall_segment_id", segment_id)
		body.set_meta("health", 100)
		body.set_meta("is_broken", false)

		var collision := CollisionShape2D.new()
		collision.name = "CollisionShape2D"
		var rectangle := RectangleShape2D.new()
		rectangle.size = Vector2(segment_length + 3.0, WALL_THICKNESS)
		collision.shape = rectangle
		collision.rotation = axis.angle()
		body.add_child(collision)
		wall_root.add_child(body)


func _build_task_areas() -> void:
	var task_root := get_node_or_null("Gameplay/TaskStations") as Node2D
	if task_root == null:
		push_warning("AsymmetricArena: Gameplay/TaskStations is missing.")
		return

	for task in TASK_STATIONS:
		var team := str(task["team"])
		var area := Area2D.new()
		area.name = str(task["id"])
		area.position = grid_to_world(Vector2(task["cell"]))
		area.collision_layer = 0
		area.collision_mask = 1
		area.monitoring = true
		area.add_to_group("task_station")
		area.add_to_group("task_team_" + team)
		area.set_meta("task_id", str(task["id"]))
		area.set_meta("task_team", team)
		area.set_meta("task_kind", str(task["kind"]))
		if task.has("wall_segment"):
			area.set_meta("linked_wall_segment", str(task["wall_segment"]))

		var interaction_shape := CollisionShape2D.new()
		var interaction_radius := CircleShape2D.new()
		interaction_radius.radius = 82.0
		interaction_shape.shape = interaction_radius
		area.add_child(interaction_shape)
		task_root.add_child(area)


func _build_spawn_markers() -> void:
	var spawn_root := get_node_or_null("Gameplay/SpawnPoints") as Node2D
	if spawn_root == null:
		push_warning("AsymmetricArena: Gameplay/SpawnPoints is missing.")
		return

	for spawn in TEAM_SPAWNS:
		var team := str(spawn["team"])
		var marker := Marker2D.new()
		marker.name = str(spawn["id"])
		marker.position = grid_to_world(Vector2(spawn["cell"]))
		marker.set_meta("team", team)
		marker.set_meta("grid_cell", spawn["cell"])
		marker.add_to_group("spawn_" + team)
		spawn_root.add_child(marker)


func _draw() -> void:
	_draw_map_footprint()
	_draw_territories()
	_draw_ground_tiles()
	_draw_service_routes()
	_draw_outer_perimeter()
	_draw_buildings()
	_draw_railway_and_train()
	_draw_wall()
	_draw_environment_props()
	_draw_spawn_zones()
	_draw_task_markers()
	_draw_map_labels()


func _draw_map_footprint() -> void:
	var corners := PackedVector2Array([
		grid_to_world(Vector2(0.0, 0.0)),
		grid_to_world(Vector2(GRID_SIZE.x, 0.0)),
		grid_to_world(Vector2(GRID_SIZE.x, GRID_SIZE.y)),
		grid_to_world(Vector2(0.0, GRID_SIZE.y)),
	])
	draw_colored_polygon(corners, Color(0.045, 0.061, 0.064, 1.0))
	_draw_closed_outline(corners, Color(0.53, 0.62, 0.58, 0.8), 5.0)


func _draw_territories() -> void:
	var zombie_zone := PackedVector2Array([
		grid_to_world(Vector2(0.0, 0.0)),
		grid_to_world(Vector2(WALL_GRID_X, 0.0)),
		grid_to_world(Vector2(WALL_GRID_X, GRID_SIZE.y)),
		grid_to_world(Vector2(0.0, GRID_SIZE.y)),
	])
	var survivor_zone := PackedVector2Array([
		grid_to_world(Vector2(WALL_GRID_X, 0.0)),
		grid_to_world(Vector2(GRID_SIZE.x, 0.0)),
		grid_to_world(Vector2(GRID_SIZE.x, GRID_SIZE.y)),
		grid_to_world(Vector2(WALL_GRID_X, GRID_SIZE.y)),
	])
	draw_colored_polygon(zombie_zone, Color(0.32, 0.12, 0.10, 0.13))
	draw_colored_polygon(survivor_zone, Color(0.08, 0.25, 0.31, 0.13))


func _draw_ground_tiles() -> void:
	for x in range(GRID_SIZE.x):
		for y in range(GRID_SIZE.y):
			var cell := Vector2i(x, y)
			var centre := grid_to_world(Vector2(float(x) + 0.5, float(y) + 0.5))
			var diamond := PackedVector2Array([
				centre + Vector2(0.0, -HALF_TILE.y),
				centre + Vector2(HALF_TILE.x, 0.0),
				centre + Vector2(0.0, HALF_TILE.y),
				centre + Vector2(-HALF_TILE.x, 0.0),
			])
			var base := _terrain_color(cell)
			draw_colored_polygon(diamond, base)
			var outline := PackedVector2Array([
				diamond[0], diamond[1], diamond[2], diamond[3], diamond[0],
			])
			draw_polyline(outline, base.lightened(0.12), 1.0)
			if _cell_hash(cell) > 0.972:
				draw_circle(centre + Vector2(7.0, -3.0), 2.5, Color(0.64, 0.56, 0.43, 0.36))


func _terrain_color(cell: Vector2i) -> Color:
	var variation := _cell_hash(cell)
	if cell.x < int(WALL_GRID_X):
		var dead_base := Color(0.105, 0.125, 0.126)
		var dead_light := Color(0.19, 0.19, 0.17)
		if cell.y < 5 or cell.y > 18:
			dead_base = Color(0.085, 0.12, 0.115)
			dead_light = Color(0.16, 0.20, 0.17)
		return dead_base.lerp(dead_light, variation * 0.72)
	var survivor_base := Color(0.16, 0.19, 0.185)
	var survivor_light := Color(0.25, 0.27, 0.245)
	if cell.x > 25:
		survivor_base = Color(0.20, 0.205, 0.18)
		survivor_light = Color(0.31, 0.29, 0.245)
	return survivor_base.lerp(survivor_light, variation * 0.7)


func _cell_hash(cell: Vector2i) -> float:
	var value := sin(float(cell.x * 127 + cell.y * 311 + 47) * 12.9898) * 43758.5453
	return value - floor(value)


func _draw_service_routes() -> void:
	_draw_iso_surface(Vector2(2.0, 10.0), Vector2(13.0, 2.0), Color(0.23, 0.24, 0.22, 0.88))
	_draw_iso_surface(Vector2(3.0, 19.0), Vector2(12.0, 1.6), Color(0.22, 0.23, 0.21, 0.88))
	_draw_iso_surface(Vector2(18.0, 3.0), Vector2(12.0, 1.7), Color(0.29, 0.29, 0.26, 0.9))
	_draw_iso_surface(Vector2(18.0, 13.0), Vector2(13.0, 1.5), Color(0.28, 0.28, 0.25, 0.9))
	_draw_iso_surface(Vector2(19.0, 21.0), Vector2(12.0, 1.2), Color(0.29, 0.28, 0.24, 0.85))


func _draw_iso_surface(origin: Vector2, size: Vector2, color: Color) -> void:
	var a := grid_to_world(origin)
	var b := grid_to_world(origin + Vector2(size.x, 0.0))
	var c := grid_to_world(origin + size)
	var d := grid_to_world(origin + Vector2(0.0, size.y))
	var polygon := PackedVector2Array([a, b, c, d])
	draw_colored_polygon(polygon, color)
	_draw_closed_outline(polygon, color.lightened(0.18), 2.0)


func _draw_outer_perimeter() -> void:
	var corners := PackedVector2Array([
		grid_to_world(Vector2(0.0, 0.0)),
		grid_to_world(Vector2(GRID_SIZE.x, 0.0)),
		grid_to_world(Vector2(GRID_SIZE.x, GRID_SIZE.y)),
		grid_to_world(Vector2(0.0, GRID_SIZE.y)),
	])
	draw_polyline(PackedVector2Array([corners[0], corners[1], corners[2], corners[3], corners[0]]), Color(0.31, 0.37, 0.34, 0.85), 8.0)
	for index in range(1, 32):
		if index % 2 == 0:
			var top_point := grid_to_world(Vector2(float(index), 0.0))
			var bottom_point := grid_to_world(Vector2(float(index), float(GRID_SIZE.y)))
			draw_circle(top_point, 4.0, Color(0.40, 0.43, 0.38, 0.85))
			draw_circle(bottom_point, 4.0, Color(0.40, 0.43, 0.38, 0.85))


func _draw_buildings() -> void:
	# Zombie territory: abandoned industrial blocks and ruined service structures.
	_draw_iso_building(Vector2(3.0, 3.5), Vector2(4.5, 4.0), Color(0.24, 0.25, 0.22), Color(0.25, 0.28, 0.26), 46.0)
	_draw_iso_building(Vector2(8.5, 9.5), Vector2(4.0, 3.5), Color(0.29, 0.25, 0.20), Color(0.30, 0.27, 0.22), 34.0)
	_draw_iso_building(Vector2(3.0, 17.5), Vector2(5.0, 3.8), Color(0.22, 0.26, 0.24), Color(0.25, 0.29, 0.27), 40.0)
	_draw_iso_building(Vector2(10.5, 19.0), Vector2(3.4, 2.5), Color(0.28, 0.24, 0.20), Color(0.31, 0.27, 0.22), 29.0)

	# Survivor territory: repair shed, service terminal, stores and platform buildings.
	_draw_iso_building(Vector2(19.0, 3.0), Vector2(4.3, 3.5), Color(0.27, 0.31, 0.29), Color(0.32, 0.34, 0.30), 46.0)
	_draw_iso_building(Vector2(24.5, 7.5), Vector2(3.5, 4.0), Color(0.32, 0.30, 0.25), Color(0.35, 0.33, 0.28), 36.0)
	_draw_iso_building(Vector2(19.0, 18.5), Vector2(3.5, 2.8), Color(0.25, 0.29, 0.28), Color(0.30, 0.33, 0.31), 32.0)
	_draw_iso_building(Vector2(27.5, 19.5), Vector2(3.0, 2.4), Color(0.29, 0.30, 0.27), Color(0.34, 0.34, 0.30), 28.0)


func _draw_iso_building(origin: Vector2, size: Vector2, roof_color: Color, wall_color: Color, height: float) -> void:
	var a := grid_to_world(origin)
	var b := grid_to_world(origin + Vector2(size.x, 0.0))
	var c := grid_to_world(origin + size)
	var d := grid_to_world(origin + Vector2(0.0, size.y))
	var lift := Vector2(0.0, -height)
	draw_colored_polygon(PackedVector2Array([d, c, c + lift, d + lift]), wall_color.darkened(0.28))
	draw_colored_polygon(PackedVector2Array([b, c, c + lift, b + lift]), wall_color.darkened(0.12))
	draw_colored_polygon(PackedVector2Array([a + lift, b + lift, c + lift, d + lift]), roof_color)
	draw_polyline(PackedVector2Array([a + lift, b + lift, c + lift, d + lift, a + lift]), wall_color.lightened(0.16), 2.0)


func _draw_railway_and_train() -> void:
	var start := grid_to_world(Vector2(21.0, 16.5))
	var finish := grid_to_world(Vector2(31.0, 16.5))
	var axis := (finish - start).normalized()
	var normal := Vector2(-axis.y, axis.x)
	draw_line(start + normal * 17.0, finish + normal * 17.0, Color(0.075, 0.082, 0.083), 10.0)
	draw_line(start - normal * 17.0, finish - normal * 17.0, Color(0.075, 0.082, 0.083), 10.0)
	draw_line(start + normal * 17.0, finish + normal * 17.0, Color(0.48, 0.47, 0.42), 4.0)
	draw_line(start - normal * 17.0, finish - normal * 17.0, Color(0.48, 0.47, 0.42), 4.0)
	for sleeper in range(1, 34):
		var point := start.lerp(finish, float(sleeper) / 34.0)
		draw_line(point - normal * 25.0, point + normal * 25.0, Color(0.20, 0.16, 0.13), 7.0)

	_draw_iso_surface(Vector2(21.0, 14.6), Vector2(11.0, 3.8), Color(0.39, 0.37, 0.31, 0.92))
	_draw_iso_building(Vector2(22.2, 15.4), Vector2(2.7, 1.6), Color(0.31, 0.36, 0.37), Color(0.18, 0.23, 0.24), 35.0)
	_draw_iso_building(Vector2(25.2, 15.4), Vector2(2.7, 1.6), Color(0.36, 0.32, 0.25), Color(0.22, 0.24, 0.23), 35.0)
	_draw_iso_building(Vector2(28.2, 15.4), Vector2(2.5, 1.6), Color(0.32, 0.35, 0.34), Color(0.20, 0.24, 0.24), 35.0)


func _draw_wall() -> void:
	var segment_step: float = float(GRID_SIZE.y) / float(WALL_SEGMENT_COUNT)
	var axis := Vector2(-HALF_TILE.x, HALF_TILE.y).normalized()
	var normal := Vector2(-axis.y, axis.x)
	for index in range(WALL_SEGMENT_COUNT):
		var start_y: float = float(index) * segment_step
		var end_y: float = float(index + 1) * segment_step
		var start := grid_to_world(Vector2(WALL_GRID_X, start_y))
		var finish := grid_to_world(Vector2(WALL_GRID_X, end_y))
		draw_line(start, finish, Color(0.055, 0.065, 0.066), 35.0)
		draw_line(start + normal * 4.0, finish + normal * 4.0, Color(0.32, 0.34, 0.31), 25.0)
		draw_line(start + normal * 8.0, finish + normal * 8.0, Color(0.48, 0.47, 0.40), 3.0)
		draw_line(start, finish, Color(0.17, 0.19, 0.18), 2.0)
		var midpoint := start.lerp(finish, 0.5)
		draw_circle(midpoint, 5.5, Color(0.70, 0.58, 0.39, 0.95))
		if index % 2 == 0:
			draw_line(midpoint + normal * 10.0, midpoint - normal * 10.0, Color(0.72, 0.58, 0.38, 0.85), 3.0)


func _draw_environment_props() -> void:
	var crate_cells: Array[Vector2i] = [
		Vector2i(2, 8), Vector2i(6, 10), Vector2i(11, 5), Vector2i(12, 16),
		Vector2i(4, 14), Vector2i(9, 21), Vector2i(19, 9), Vector2i(22, 12),
		Vector2i(27, 5), Vector2i(30, 13), Vector2i(20, 20), Vector2i(26, 21),
	]
	for cell in crate_cells:
		var point := grid_to_world(Vector2(cell))
		var crate_color := Color(0.34, 0.27, 0.19)
		if cell.x >= int(WALL_GRID_X):
			crate_color = Color(0.31, 0.29, 0.23)
		_draw_iso_building(Vector2(cell), Vector2(0.75, 0.65), crate_color, crate_color.darkened(0.35), 16.0)


func _draw_spawn_zones() -> void:
	for spawn in TEAM_SPAWNS:
		var point := grid_to_world(Vector2(spawn["cell"]))
		var color := TEAM_ZOMBIE if str(spawn["team"]) == "zombies" else TEAM_SURVIVOR
		draw_circle(point, 29.0, Color(color.r, color.g, color.b, 0.13))
		draw_arc(point, 31.0, 0.0, TAU, 32, color, 3.0)
		draw_circle(point, 7.0, color)


func _draw_task_markers() -> void:
	for task in TASK_STATIONS:
		var point := grid_to_world(Vector2(task["cell"]))
		var color := TEAM_ZOMBIE if str(task["team"]) == "zombies" else TEAM_SURVIVOR
		draw_circle(point, 22.0, Color(color.r, color.g, color.b, 0.18))
		draw_arc(point, 25.0, 0.0, TAU, 32, color, 3.0)
		draw_circle(point, 6.0, color)
		draw_string(
			ThemeDB.fallback_font,
			point + Vector2(34.0, -8.0),
			str(task["label"]),
			HORIZONTAL_ALIGNMENT_LEFT,
			-1,
			22,
			Color(0.93, 0.94, 0.90, 0.98)
		)


func _draw_map_labels() -> void:
	draw_string(
		ThemeDB.fallback_font,
		Vector2(150.0, 112.0),
		"REDLINE  /  ASYMMETRIC QUARANTINE ARENA",
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
		42,
		Color(0.92, 0.94, 0.89, 1.0)
	)
	draw_string(
		ThemeDB.fallback_font,
		Vector2(150.0, 153.0),
		"DEVELOPMENT BLOCKOUT  •  NOT FINAL ENVIRONMENT ART",
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
		24,
		Color(0.68, 0.75, 0.71, 0.92)
	)
	var zombie_label := grid_to_world(Vector2(7.5, 11.8))
	var survivor_label := grid_to_world(Vector2(24.5, 11.8))
	draw_string(ThemeDB.fallback_font, zombie_label + Vector2(-90.0, -105.0), "THE DEAD", HORIZONTAL_ALIGNMENT_CENTER, 240.0, 36, TEAM_ZOMBIE)
	draw_string(ThemeDB.fallback_font, survivor_label + Vector2(-50.0, -105.0), "SURVIVORS", HORIZONTAL_ALIGNMENT_CENTER, 240.0, 36, TEAM_SURVIVOR)
	draw_string(
		ThemeDB.fallback_font,
		grid_to_world(Vector2(16.0, 12.0)) + Vector2(20.0, -32.0),
		"BREAKABLE WALL",
		HORIZONTAL_ALIGNMENT_CENTER,
		-1,
		24,
		Color(0.91, 0.82, 0.63, 0.95)
	)


func _draw_closed_outline(points: PackedVector2Array, color: Color, width: float) -> void:
	var closed_points := points.duplicate()
	if not closed_points.is_empty():
		closed_points.append(closed_points[0])
	draw_polyline(closed_points, color, width)
