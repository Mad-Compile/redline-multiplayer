extends Control
## REDLINE home menu. Artwork is a verified, directly bundled WebP texture split
## into binary resource chunks so Android can load it without ZIP filesystem APIs.

const MENU_ART_PARTS := 20

var _background: TextureRect
var _practice_button: Button
var _match_button: Button
var _settings_button: Button
var _overlay: ColorRect
var _overlay_panel: PanelContainer

func _ready() -> void:
	_build_background()
	_build_menu_buttons()
	_build_overlay()
	_layout()
	get_viewport().size_changed.connect(_layout)

func _load_menu_texture() -> Texture2D:
	var image_bytes := PackedByteArray()
	for part_index in range(MENU_ART_PARTS):
		var path := "res://assets/menu/menu_art_%02d.dat" % part_index
		var part_bytes := FileAccess.get_file_as_bytes(path)
		if part_bytes.is_empty():
			push_error("REDLINE menu: missing bundled art chunk: " + path)
			return null
		image_bytes.append_array(part_bytes)
	var image := Image.new()
	var error := image.load_webp_from_buffer(image_bytes)
	if error != OK:
		push_error("REDLINE menu: bundled WebP could not be decoded (error %s)." % error)
		return null
	return ImageTexture.create_from_image(image)

func _build_background() -> void:
	_background = TextureRect.new()
	_background.name = "Terminal09MenuArtwork"
	_background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_background.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_background.stretch_mode = TextureRect.STRETCH_SCALE
	_background.texture = _load_menu_texture()
	_background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_background)
	move_child(_background, 0)

func _make_hotspot(label: String) -> Button:
	var button := Button.new()
	button.name = label.replace(" ", "") + "HitArea"
	button.text = ""
	button.focus_mode = Control.FOCUS_ALL
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var normal := StyleBoxEmpty.new()
	var hover := StyleBoxFlat.new()
	hover.bg_color = Color(1.0, 0.44, 0.12, 0.09)
	hover.border_color = Color(1.0, 0.42, 0.12, 0.92)
	hover.set_border_width_all(2)
	var pressed := StyleBoxFlat.new()
	pressed.bg_color = Color(1.0, 0.30, 0.08, 0.22)
	pressed.border_color = Color(1.0, 0.58, 0.25, 1.0)
	pressed.set_border_width_all(3)
	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("focus", normal)
	button.add_theme_stylebox_override("hover", hover)
	button.add_theme_stylebox_override("pressed", pressed)
	return button

func _build_menu_buttons() -> void:
	_practice_button = _make_hotspot("Practice")
	_practice_button.pressed.connect(_on_practice)
	add_child(_practice_button)
	_match_button = _make_hotspot("Start Match")
	_match_button.pressed.connect(_on_start_match)
	add_child(_match_button)
	_settings_button = _make_hotspot("Settings")
	_settings_button.pressed.connect(_on_settings)
	add_child(_settings_button)

func _build_overlay() -> void:
	_overlay = ColorRect.new()
	_overlay.name = "MenuOverlay"
	_overlay.color = Color(0.012, 0.016, 0.019, 0.91)
	_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_overlay.visible = false
	_overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_overlay)
	_overlay_panel = PanelContainer.new()
	_overlay_panel.name = "IndustrialDialog"
	var panel_style := StyleBoxFlat.new()
	panel_style.bg_color = Color(0.055, 0.061, 0.061, 0.99)
	panel_style.border_color = Color(0.69, 0.25, 0.11, 1.0)
	panel_style.set_border_width_all(3)
	panel_style.set_corner_radius_all(3)
	panel_style.content_margin_left = 34
	panel_style.content_margin_right = 34
	panel_style.content_margin_top = 30
	panel_style.content_margin_bottom = 30
	_overlay_panel.add_theme_stylebox_override("panel", panel_style)
	_overlay.add_child(_overlay_panel)

func _layout() -> void:
	if not is_inside_tree() or _practice_button == null:
		return
	var viewport_size := get_viewport_rect().size
	var sx := viewport_size.x / 1600.0
	var sy := viewport_size.y / 900.0
	_practice_button.position = Vector2(965.0 * sx, 172.0 * sy)
	_practice_button.size = Vector2(526.0 * sx, 157.0 * sy)
	_match_button.position = Vector2(830.0 * sx, 355.0 * sy)
	_match_button.size = Vector2(699.0 * sx, 139.0 * sy)
	_settings_button.position = Vector2(965.0 * sx, 560.0 * sy)
	_settings_button.size = Vector2(540.0 * sx, 167.0 * sy)
	var scale_factor := minf(sx, sy)
	var panel_size := Vector2(680, 390) * scale_factor
	_overlay_panel.custom_minimum_size = panel_size
	_overlay_panel.size = panel_size
	_overlay_panel.position = viewport_size * 0.5 - panel_size * 0.5

func _on_practice() -> void:
	_show_message(
		"PRACTICE MODE IN DEVELOPMENT",
		"Terminal 09 is being connected to player movement, character animations and interactive objectives. Practice will open when that space is playable.",
		"BACK"
	)

func _on_start_match() -> void:
	_show_message(
		"MULTIPLAYER CONNECTION",
		"The peer-to-peer engine is being developed separately. The REDLINE lobby will connect when its integration interface is available.",
		"BACK"
	)

func _on_settings() -> void:
	_show_settings()

func _show_message(title_text: String, body_text: String, button_text: String) -> void:
	_show_overlay()
	var column := _new_overlay_column()
	_add_overlay_title(column, title_text)
	var body := Label.new()
	body.text = body_text
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.custom_minimum_size = Vector2(0, 110)
	body.add_theme_font_size_override("font_size", 19)
	body.add_theme_color_override("font_color", Color(0.82, 0.83, 0.79))
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
		DisplayServer.window_set_mode(
			DisplayServer.WINDOW_MODE_FULLSCREEN if enabled else DisplayServer.WINDOW_MODE_WINDOWED
		)
	)
	column.add_child(fullscreen)
	_add_overlay_back(column, "BACK")

func _show_overlay() -> void:
	for child in _overlay_panel.get_children():
		_overlay_panel.remove_child(child)
		child.queue_free()
	_overlay.visible = true
	_layout()

func _new_overlay_column() -> VBoxContainer:
	var column := VBoxContainer.new()
	column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	column.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_theme_constant_override("separation", 22)
	_overlay_panel.add_child(column)
	return column

func _add_overlay_title(parent: VBoxContainer, title_text: String) -> void:
	var title := Label.new()
	title.text = title_text
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title.add_theme_font_size_override("font_size", 27)
	title.add_theme_color_override("font_color", Color(0.91, 0.72, 0.48))
	parent.add_child(title)

func _add_overlay_back(parent: VBoxContainer, button_text: String) -> void:
	var back := Button.new()
	back.text = button_text
	back.custom_minimum_size = Vector2(0, 54)
	back.add_theme_font_size_override("font_size", 20)
	back.pressed.connect(func() -> void: _overlay.visible = false)
	parent.add_child(back)

func _unhandled_input(event: InputEvent) -> void:
	if _overlay != null and _overlay.visible and event.is_action_pressed("ui_cancel"):
		_overlay.visible = false
		get_viewport().set_input_as_handled()
