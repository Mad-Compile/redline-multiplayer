extends Node2D
## Terminal 09 is the first REDLINE map blockout.
## Procedural terrain and structure guides are greybox composition aids, not final environment art.

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
	_draw_ground_tiles()
	_draw_service_routes()
	_draw_rail_network()
	_draw_platforms_and_structures()
	_draw_yard_props()
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


## Procedural visual foundation: readable greybox forms, not final art.
func _draw_ground_tiles() -> void:
	for x in range(GRID_SIZE.x):
		for y in range(GRID_SIZE.y):
			var cell := Vector2i(x, y)
			var center := grid_to_world(Vector2(x + 0.5, y + 0.5))
			var diamond := PackedVector2Array([center + Vector2(0, -32), center + Vector2(64, 0), center + Vector2(0, 32), center + Vector2(-64, 0), center + Vector2(0, -32)])
			var base := _terrain_color(cell)
			draw_colored_polygon(diamond, base)
			draw_polyline(diamond, Color(base.lightened(0.10), 0.32), 1.0)
			if _cell_hash(cell) > 0.965:
				draw_circle(center + Vector2(8, -4), 2.0, Color(0.48, 0.43, 0.32, 0.55))


func _terrain_color(cell: Vector2i) -> Color:
	var n := _cell_hash(cell)
	if cell.x < 6 and cell.y > 13:
		return Color(0.10, 0.20, 0.20).lerp(Color(0.14, 0.25, 0.24), n)
	if cell.y < 5 or cell.x > 32:
		return Color(0.15, 0.19, 0.17).lerp(Color(0.22, 0.25, 0.21), n)
	if cell.x >= 12 and cell.x <= 26 and cell.y >= 6 and cell.y <= 18:
		return Color(0.25, 0.25, 0.23).lerp(Color(0.32, 0.30, 0.26), n)
	if cell.x >= 25 and cell.y >= 10:
		return Color(0.30, 0.29, 0.25).lerp(Color(0.38, 0.35, 0.29), n)
	return Color(0.16, 0.21, 0.18).lerp(Color(0.22, 0.27, 0.21), n)


func _cell_hash(cell: Vector2i) -> float:
	var v := sin(float(cell.x * 127 + cell.y * 311 + 47) * 12.9898) * 43758.5453
	return v - floor(v)


func _draw_service_routes() -> void:
	_draw_iso_rect(Vector2i(7, 13), Vector2i(21, 2), Color(0.34, 0.32, 0.27), Color(0.49, 0.44, 0.34))
	_draw_iso_rect(Vector2i(11, 17), Vector2i(17, 2), Color(0.32, 0.30, 0.26), Color(0.45, 0.40, 0.32))
	_draw_iso_rect(Vector2i(8, 8), Vector2i(3, 7), Color(0.31, 0.31, 0.28), Color(0.44, 0.42, 0.36))


func _draw_rail_network() -> void:
	for track_y in [7, 10, 13, 16]:
		var left := grid_to_world(Vector2(13, float(track_y)))
		var right := grid_to_world(Vector2(35, float(track_y)))
		var axis := (right - left).normalized()
		var normal := Vector2(-axis.y, axis.x)
		draw_polyline(PackedVector2Array([left + normal * 13, right + normal * 13]), Color(0.075, 0.082, 0.083), 9)
		draw_polyline(PackedVector2Array([left - normal * 13, right - normal * 13]), Color(0.075, 0.082, 0.083), 9)
		draw_polyline(PackedVector2Array([left + normal * 13, right + normal * 13]), Color(0.48, 0.49, 0.45), 4)
		draw_polyline(PackedVector2Array([left - normal * 13, right - normal * 13]), Color(0.48, 0.49, 0.45), 4)
		for step in range(1, 22):
			var p := left.lerp(right, float(step) / 22.0)
			draw_line(p + normal * 22, p - normal * 22, Color(0.19, 0.15, 0.12), 7)
	var siding := PackedVector2Array([grid_to_world(Vector2(20, 7)), grid_to_world(Vector2(24, 10)), grid_to_world(Vector2(28, 10))])
	draw_polyline(siding, Color(0.075, 0.082, 0.083), 9)
	draw_polyline(siding, Color(0.48, 0.49, 0.45), 4)


func _draw_platforms_and_structures() -> void:
	_draw_iso_rect(Vector2i(3, 15), Vector2i(10, 8), Color(0.16, 0.20, 0.18), Color(0.40, 0.39, 0.33))
	_draw_iso_rect(Vector2i(4, 16), Vector2i(5, 4), Color(0.12, 0.16, 0.16), Color(0.34, 0.35, 0.32))
	_draw_iso_rect(Vector2i(4, 6), Vector2i(7, 6), Color(0.14, 0.17, 0.16), Color(0.43, 0.39, 0.31))
	_draw_iso_rect(Vector2i(26, 11), Vector2i(8, 3), Color(0.18, 0.19, 0.18), Color(0.49, 0.45, 0.36))
	_draw_iso_rect(Vector2i(27, 15), Vector2i(7, 5), Color(0.16, 0.18, 0.17), Color(0.39, 0.39, 0.35))
	_draw_iso_rect(Vector2i(25, 10), Vector2i(10, 2), Color(0.36, 0.34, 0.29), Color(0.58, 0.54, 0.44))


func _draw_iso_rect(origin: Vector2i, size: Vector2i, top_color: Color, edge_color: Color) -> void:
	var a := grid_to_world(Vector2(origin))
	var b := grid_to_world(Vector2(origin + Vector2i(size.x, 0)))
	var c := grid_to_world(Vector2(origin + size))
	var d := grid_to_world(Vector2(origin + Vector2i(0, size.y)))
	var depth := Vector2(0, 18)
	draw_colored_polygon(PackedVector2Array([d, c, c + depth, d + depth]), edge_color.darkened(0.25))
	draw_colored_polygon(PackedVector2Array([b, c, c + depth, b + depth]), edge_color.darkened(0.12))
	draw_colored_polygon(PackedVector2Array([a, b, c, d]), top_color)
	draw_polyline(PackedVector2Array([a, b, c, d, a]), edge_color, 2)


func _draw_yard_props() -> void:
	for cell in [Vector2i(15, 8), Vector2i(17, 17), Vector2i(23, 8), Vector2i(24, 16), Vector2i(30, 19)]:
		var p := grid_to_world(Vector2(cell))
		var top := PackedVector2Array([p + Vector2(0, -17), p + Vector2(27, -4), p + Vector2(0, 9), p + Vector2(-27, -4)])
		draw_colored_polygon(top, Color(0.40, 0.31, 0.20))
		draw_colored_polygon(PackedVector2Array([top[3], top[2], top[2] + Vector2(0, 15), top[3] + Vector2(0, 15)]), Color(0.17, 0.14, 0.11))
		draw_colored_polygon(PackedVector2Array([top[1], top[2], top[2] + Vector2(0, 15), top[1] + Vector2(0, 15)]), Color(0.25, 0.20, 0.14))
		draw_polyline(PackedVector2Array([top[0], top[1], top[2], top[3], top[0]]), Color(0.10, 0.10, 0.09), 2)
	for cell in [Vector2i(14, 5), Vector2i(19, 4), Vector2i(24, 5)]:
		var p := grid_to_world(Vector2(cell))
		var top := PackedVector2Array([p + Vector2(0, -26), p + Vector2(48, -5), p + Vector2(0, 16), p + Vector2(-48, -5)])
		draw_colored_polygon(PackedVector2Array([top[3], top[2], top[2] + Vector2(0, 37), top[3] + Vector2(0, 37)]), Color(0.12, 0.16, 0.15))
		draw_colored_polygon(PackedVector2Array([top[1], top[2], top[2] + Vector2(0, 37), top[1] + Vector2(0, 37)]), Color(0.17, 0.20, 0.19))
		draw_colored_polygon(top, Color(0.29, 0.35, 0.31))
		draw_polyline(PackedVector2Array([top[0], top[1], top[2], top[3], top[0]]), Color(0.07, 0.08, 0.08), 2)
