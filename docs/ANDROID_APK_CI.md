# Android APK CI verification

This page documents the Python/Kivy Android packaging path.

- Active runtime: Python 3.11+ and Kivy 2.3.1.
- Android packager: Buildozer / python-for-android.
- APK target: arm64-v8a debug build, Android API 35 (minimum API 24).
- Workflow: `.github/workflows/python-android-apk.yml`.
- Required gates: Python compilation, Kivy app startup smoke test, the MAP 01 39-location viewer smoke test, and pytest.
- Artifact: `REDLINE-Android-Debug-APK`, containing the installable APK and a SHA-256 checksum. GitHub retains the artifact for 30 days.

The package is the current Python branch app. It includes the image-backed menu buttons and the source-derived MAP 01 schematic viewer. It does not imply that character movement, collision, zombie navigation/AI, multiplayer transport, or the full escape match loop are complete.
