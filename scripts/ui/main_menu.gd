extends Control
## REDLINE home menu. Production button art is loaded from res://assets/menu/.
## If an art file is absent, the menu remains navigable and reports the missing asset.

const ARENA_SCENE := "res://scenes/maps/asymmetric_arena/asymmetric_arena_map.tscn"
const BG_PATH := "res://assets/menu/menu_background.webp"
const PRACTICE_PATH := "res://assets/menu/practice_button.webp"
const MATCH_PATH := "res://assets/menu/start_match_button.webp"
const SETTINGS_PATH := "res://assets/menu/settings_button.webp"

var background: TextureRect
var practice_button: TextureButton
var match_button: TextureButton
var settings_button: TextureButton
var overlay: ColorRect
var overlay_panel: PanelContainer
var missing_assets: Array[String] = []

func _ready() -> void:
	_build_background()
	_build_menu_buttons()
	_build_overlay()
	_layout()
	get_viewport().size_changed.connect(_layout)

func _build_background() -> void:
	background = TextureRect.new()
	background.name = "Terminal09Background"
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	background.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	var texture := load(BG_PATH) as Texture2D
	if texture:
		background.texture = texture
	else:
		missing_assets.append(BG_PATH)
		background.modulate = Color(0.10, 0.12, 0.13)
	add_child(background)
	move_child(background, 0)

func _build_menu_buttons() -> void:
	practice_button = _make_art_button("Practice", PRACTICE_PATH)
	practice_button.pressed.connect(_on_practice)
	add_child(practice_button)
	match_button = _make_art_button("Start Match", MATCH_PATH)
	match_button.pressed.connect(_on_start_match)
	add_child(match_button)
	settings_button = _make_art_button("Settings", SETTINGS_PATH)
	settings_button.pressed.connect(_on_settings)
	add_child(settings_button)

func _make_art_button(label: String, path: String) -> TextureButton:
	var button := TextureButton.new()
	button.name = label.replace(" ", "") + "Button"
	button.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
	button.ignore_texture_size = true
	button.focus_mode = Control.FOCUS_ALL
	var texture := load(path) as Texture2D
	if texture:
		button.texture_normal = texture
		button.texture_hover = texture
		button.texture_pressed = texture
	else:
		missing_assets.append(path)
		var fallback := Button.new()
		fallback.text = label.to_upper()
		fallback.add_theme_font_size_override("font_size", 30)
		fallback.add_theme_color_override("font_color", Color(0.94, 0.88, 0.76))
		fallback.add_theme_color_override("font_hover_color", Color.WHITE)
		fallback.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		button.add_child(fallback)
		fallback.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return button

func _build_overlay() -> void:
	overlay = ColorRect.new()
	overlay.name = "MenuOverlay"
	overlay.color = Color(0.015, 0.02, 0.025, 0.88)
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.visible = false
	overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(overlay)
	overlay_panel = PanelContainer.new()
	overlay_panel.position = Vector2(460, 250)
	overlay_panel.size = Vector2(680, 400)
	overlay.add_child(overlay_panel)

func _layout() -> void:
	if not is_inside_tree():
		return
	var viewport_size := get_viewport_rect().size
	var scale_factor := minf(viewport_size.x / 1600.0, viewport_size.y / 900.0)
	var right_edge := viewport_size.x - 54.0 * scale_factor
	practice_button.size = Vector2(590, 176) * scale_factor
	practice_button.position = Vector2(right_edge - practice_button.size.x, 160.0 * scale_factor)
	match_button.size = Vector2(690, 137) * scale_factor
	match_button.position = Vector2(right_edge - match_button.size.x, 355.0 * scale_factor)
	settings_button.size = Vector2(590, 182) * scale_factor
	settings_button.position = Vector2(right_edge - settings_button.size.x, 525.0 * scale_factor)
	overlay_panel.position = viewport_size * 0.5 - overlay_panel.size * 0.5

func _on_practice() -> void:
	get_tree().change_scene_to_file(ARENA_SCENE)

func _on_start_match() -> void:
	_show_message("ONLINE MATCH UNAVAILABLE", "The P2P engine is being developed separately. REDLINE will connect to it when its integration package is ready.", "BACK")

func _on_settings() -> void:
	_show_settings()

func _show_message(title_text: String, body_text: String, button_text: String) -> void:
	_show_overlay()
	var column := _new_overlay_column()
	_add_overlay_title(column, title_text)
	var body := Label.new()
	body.text = body_text
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size = Vector2(560, 100)
	column.add_child(body)
	_add_overlay_back(column, button_text)

func _show_settings() -> void:
	_show_overlay()
	var column := _new_overlay_column()
	_add_overlay_title(column, "FIELD SETTINGS")
	var volume_label := Label.new()
	volume_label.text = "MASTER VOLUME"
	column.add_child(volume_label)
	var volume := HSlider.new()
	volume.min_value = 0.0
	volume.max_value = 1.0
	volume.step = 0.05
	volume.value = db_to_linear(AudioServer.get_bus_volume_db(0))
	volume.value_changed.connect(func(value: float) -> void:
		AudioServer.set_bus_volume_db(0, linear_to_db(maxf(value, 0.001)))
	)
	column.add_child(volume)
	var fullscreen := CheckButton.new()
	fullscreen.text = "FULLSCREEN"
	fullscreen.button_pressed = DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
	fullscreen.toggled.connect(func(enabled: bool) -> void:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if enabled else DisplayServer.WINDOW_MODE_WINDOWED)
	)
	column.add_child(fullscreen)
	_add_overlay_back(column, "BACK")

func _show_overlay() -> void:
	for child in overlay_panel.get_children():
		child.queue_free()
	overlay.visible = true
	_layout()

func _new_overlay_column() -> VBoxContainer:
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 22)
	overlay_panel.add_child(column)
	return column

func _add_overlay_title(parent: VBoxContainer, title_text: String) -> void:
	var title := Label.new()
	title.text = title_text
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size",  thirty_two())
	parent.add_child(title)

func thirty_two() -> int:
	return 32

func _add_overlay_back(parent: VBoxContainer, button_text: String) -> void:
	var back := Button.new()
	back.text = button_text
	back.custom_minimum_size = Vector2(0, 58)
	back.pressed.connect(func() -> void: overlay.visible = false)
	parent.add_child(back)
