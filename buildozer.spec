[app]
title = REDLINE
package.name = redline
package.domain = com.madcompile
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,webp,zip,mp3,ttf,json
source.exclude_dirs = .git,.github,.pytest_cache,__pycache__,tests,bin,.venv
version = 0.1.0
requirements = python3,kivy==2.3.1,pillow
orientation = landscape
fullscreen = 1
android.api = 35
android.minapi = 24
android.archs = arm64-v8a
android.permissions = INTERNET
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
