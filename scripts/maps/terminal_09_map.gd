extends Node2D
## Terminal 09 is the first REDLINE map blockout.
## The coloured overlay is a development aid; it is not final environment art.

const GRID_SIZE := Vector2i(36, 24)
const TILE_SIZE := Vector2i(128, 64)
const HALF_TILE := Vector2(64.0, 32.0)
const GRID_ORIGIN := Vector2(1536.0, 0.0)

const ZONES: Array[Dictionary] = [
	{
		"id": "secure_compound",
		"label": "SECURE MAINTENANCE COMPOUND",
		"origin": Vector2i(3, 15),
		"size": Vector2i(10, 8),
		"color": Color(0.16, 0.42, 0.34, 0.28),
	},
	{
		"id": "generator_shed",
		"label": "GENERATOR / SERVICE SHED",
		"origin": Vector2i(3, 6),
		"size": Vector2i(9, 8),
		"color": Color(0.52, 0.38, 0.16, 0.25),
	},
	{
		"id": "switching_yard",
		"label": "CENTRAL SWITCHING YARD",
		"origin": Vector2i(12, 6),
		"size": Vector2i(14, 13),
		"color": Color(0.25, 0.36, 0.49, 0.23),
	},
	{
		"id": "freight_approach",
		"label": "NORTH FREIGHT APPROACH",
		"origin": Vector2i(11, 0),
		"size": Vector2i(18, 7),
		"color": Color(0.48, 0.20, 0.19, 0.23),
	},
	{
		"id": "passenger_platform",
		"label": "PASSENGER PLATFORM / EXTRACTION",
		"origin": Vector2i(25, 10),
		"size": Vector2i(10, 12),
		"color": Color(0.35, 0.34, 0.49, 0.25),
	},
	{
		"id": "drainage_route",
		"label": "WEST DRAINAGE ROUTE",
		"origin": Vector2i(0, 13),
		"size": Vector2i(7, 10),
		"color": Color(0.19, 0.39, 0.43, 0.25),
	},
]

const MAP_POINTS: Array[Dictionary] = [
	{"id": "survivor_start", "label": "SURVIVOR START", "cell": Vector2i(7, 18), "kind": "survivor"},
	{"id": "infected_spawn_north", "label": "INFECTED ENTRY — NORTH", "cell": Vector2i(18, 1), "kind": "infected"},
	{"id": "infected_spawn_west", "label": "INFECTED ENTRY — WEST", "cell": Vector2i(1, 15), "kind": "infected"},
	{"id": "infected_spawn_east", "label": "INFECTED ENTRY — EAST", "cell": Vector2i(34, 19), "kind": "infected"},
	{"id": "breach_freight_gate", "label": "BREACH — FREIGHT GATE", "cell": Vector2i(18, 6), "kind": "breach"},
	{"id": "breach_west_drain", "label": "BREACH — DRAIN", "cell": Vector2i(5, 18), "kind": "breach"},
	{"id": "breach_platform_tunnel", "label": "BREACH — PLATFORM TUNNEL", "cell": Vector2i(29, 18), "kind": "breach"},
	{"id": "objective_generator", "label": "OBJECTIVE — GENERATOR", "cell": Vector2i(8, 9), "kind": "objective"},
	{"id": "objective_track_switch", "label": "OBJECTIVE — TRACK SWITCH", "cell": Vector2i(21, 11), "kind": "objective"},
	{"id": "objective_locomotive_fuel", "label": "OBJECTIVE — LOCOMOTIVE FUEL", "cell": Vector2i(28, 16), "kind": "objective"},
	{"id": "extraction_train", "label": "EXTRACTION — TRAIN", "cell": Vector2i(32, 13), "kind": "extraction"},
]

@export var draw_debug_blockout: bool = true


func _ready() -> void:
	_build_map_markers()
	queue_redraw()


## Convert a cell coordinate into its isometric screen-space centre.
## The two grid axes project down-right and down-left respectively.
func grid_to_world(cell: Vector2) -> Vector2:
	return GRID_ORIGIN + Vector2(
		(cell.x - cell.y) * HALF_TILE.x,
		(cell.x + cell.y) * HALF_TILE.y
	)


func _build_map_markers() -> void:
	var marker_root := get_node_or_null("Gameplay/MapMarkers") as Node2D
	if marker_root == null:
		push_warning("Terminal09: Gameplay/MapMarkers was not found.")
		return

	for point in MAP_POINTS:
		var marker := Marker2D.new()
		marker.name = str(point["id"])
		marker.position = grid_to_world(Vector2(point["cell"]))
		marker.set_meta("map_point_id", str(point["id"]))
		marker.set_meta("map_point_kind", str(point["kind"]))
		marker.set_meta("grid_cell", point["cell"])
		marker.add_to_group("map_point_" + str(point["kind"]))
		marker_root.add_child(marker)


func _draw() -> void:
	if not draw_debug_blockout:
		return

	_draw_map_footprint()
	_draw_zone_overlays()
	_draw_grid()
	_draw_map_points()
	_draw_debug_title()


func _draw_map_footprint() -> void:
	var corners := PackedVector2Array([
		grid_to_world(Vector2(0.0, 0.0)),
		grid_to_world(Vector2(GRID_SIZE.x, 0.0)),
		grid_to_world(Vector2(GRID_SIZE.x, GRID_SIZE.y)),
		grid_to_world(Vector2(0.0, GRID_SIZE.y)),
	])
	draw_colored_polygon(corners, Color(0.075, 0.105, 0.105, 1.0))
	_draw_closed_outline(corners, Color(0.55, 0.68, 0.62, 0.75), 4.0)


func _draw_zone_overlays() -> void:
	for zone in ZONES:
		var origin: Vector2i = zone["origin"]
		var size: Vector2i = zone["size"]
		var polygon := PackedVector2Array([
			grid_to_world(Vector2(origin)),
			grid_to_world(Vector2(origin + Vector2i(size.x, 0))),
			grid_to_world(Vector2(origin + size)),
			grid_to_world(Vector2(origin + Vector2i(0, size.y))),
		])
		var zone_color: Color = zone["color"]
		draw_colored_polygon(polygon, zone_color)
		_draw_closed_outline(polygon, zone_color.lightened(0.55), 2.0)

		var label_position := grid_to_world(Vector2(origin) + Vector2(size) * 0.5)
		draw_string(
			ThemeDB.fallback_font,
			label_position,
			str(zone["label"]),
			HORIZONTAL_ALIGNMENT_CENTER,
			-1,
			16,
			Color(0.88, 0.92, 0.87, 0.88)
		)


func _draw_grid() -> void:
	var grid_color := Color(0.72, 0.80, 0.75, 0.12)
	for x in range(GRID_SIZE.x):
		for y in range(GRID_SIZE.y):
			var center := grid_to_world(Vector2(x + 0.5, y + 0.5))
			var diamond := PackedVector2Array([
				center + Vector2(0.0, -HALF_TILE.y),
				center + Vector2(HALF_TILE.x, 0.0),
				center + Vector2(0.0, HALF_TILE.y),
				center + Vector2(-HALF_TILE.x, 0.0),
				center + Vector2(0.0, -HALF_TILE.y),
			])
			draw_polyline(diamond, grid_color, 1.0)


func _draw_map_points() -> void:
	for point in MAP_POINTS:
		var position := grid_to_world(Vector2(point["cell"]))
		var kind := str(point["kind"])
		var marker_color := _point_color(kind)

		draw_circle(position, 10.0, marker_color)
		draw_arc(position, 16.0, 0.0, TAU, 24, marker_color, 2.0)
		draw_string(
			ThemeDB.fallback_font,
			position + Vector2(19.0, -7.0),
			str(point["label"]),
			HORIZONTAL_ALIGNMENT_LEFT,
			-1,
			14,
			Color(0.94, 0.95, 0.90, 0.95)
		)


func _draw_debug_title() -> void:
	draw_string(
		ThemeDB.fallback_font,
		Vector2(110.0, 120.0),
		"TERMINAL 09  /  QUARANTINE RAIL YARD",
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
		28,
		Color(0.93, 0.95, 0.90, 1.0)
	)
	draw_string(
		ThemeDB.fallback_font,
		Vector2(110.0, 158.0),
		"DEVELOPMENT BLOCKOUT — NOT FINAL ENVIRONMENT ART",
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
		16,
		Color(0.72, 0.79, 0.75, 0.9)
	)


func _draw_closed_outline(points: PackedVector2Array, color: Color, width: float) -> void:
	var closed_points := points.duplicate()
	if not closed_points.is_empty():
		closed_points.append(closed_points[0])
	draw_polyline(closed_points, color, width)


func _point_color(kind: String) -> Color:
	match kind:
		"survivor":
			return Color(0.35, 0.95, 0.66, 1.0)
		"infected":
			return Color(0.95, 0.31, 0.25, 1.0)
		"breach":
			return Color(1.0, 0.58, 0.23, 1.0)
		"objective":
			return Color(0.36, 0.70, 1.0, 1.0)
		"extraction":
			return Color(1.0, 0.84, 0.33, 1.0)
		_:
			return Color.WHITE
