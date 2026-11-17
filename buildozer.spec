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

# Pin python-for-android to the upstream fix for its build-venv pip self-upgrade
# issue (#3360). The current default master branch still hits the broken path.
p4a.branch = develop
p4a.commit = 0382d27de2f7315ed98e74884bafb30365decdee

[buildozer]
log_level = 2
warn_on_root = 1
