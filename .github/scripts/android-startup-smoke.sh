#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

APK_DIR="$REPO_ROOT/emulator-apk"
DIAG_DIR="$REPO_ROOT/android-startup-diagnostics"
mkdir -p "$DIAG_DIR"

echo "APK download contents:"
find "$APK_DIR" -maxdepth 4 -type f -print -ls
APK="$(find "$APK_DIR" -maxdepth 4 -type f -name '*.apk' -print -quit)"
if [[ -z "$APK" ]]; then
  echo "::error::No APK was found under $APK_DIR"
  exit 1
fi

echo "Installing REDLINE APK: $APK"
adb wait-for-device
for attempt in $(seq 1 60); do
  BOOTED="$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
  [[ "$BOOTED" == "1" ]] && break
  sleep 2
done
if [[ "${BOOTED:-}" != "1" ]]; then
  echo "::error::Android emulator did not finish booting"
  exit 1
fi

adb install -r "$APK"
adb logcat -c
adb shell am force-stop com.madcompile.redline || true
adb shell monkey -p com.madcompile.redline -c android.intent.category.LAUNCHER 1

PID=""
for attempt in $(seq 1 45); do
  PID="$(adb shell pidof com.madcompile.redline 2>/dev/null | tr -d '\r' || true)"
  if [[ -n "$PID" ]]; then
    break
  fi
  sleep 1
done
adb logcat -d -b all > "$DIAG_DIR/android-startup-logcat.txt"
adb exec-out screencap -p > "$DIAG_DIR/android-startup-screen.png" || true

if [[ -z "$PID" ]]; then
  echo "::error::REDLINE process exited during initial startup"
  tail -n 500 "$DIAG_DIR/android-startup-logcat.txt"
  exit 1
fi

sleep 15
PID_AFTER_WAIT="$(adb shell pidof com.madcompile.redline 2>/dev/null | tr -d '\r' || true)"
adb logcat -d -b all > "$DIAG_DIR/android-startup-logcat.txt"
adb exec-out screencap -p > "$DIAG_DIR/android-startup-screen.png" || true

if [[ -z "$PID_AFTER_WAIT" ]]; then
  echo "::error::REDLINE process died during the 15-second startup observation"
  tail -n 500 "$DIAG_DIR/android-startup-logcat.txt"
  exit 1
fi

if grep -Eiq 'FATAL EXCEPTION|SIGSEGV|Fatal signal|REDLINE: fatal exception while constructing the main menu' "$DIAG_DIR/android-startup-logcat.txt"; then
  echo "::error::Fatal startup error found in Android logcat"
  tail -n 500 "$DIAG_DIR/android-startup-logcat.txt"
  exit 1
fi

if ! grep -Fq 'REDLINE: main menu constructed successfully' "$DIAG_DIR/android-startup-logcat.txt"; then
  echo "::error::Process remained alive, but main-menu construction was not confirmed"
  tail -n 500 "$DIAG_DIR/android-startup-logcat.txt"
  exit 1
fi

echo "PASS: REDLINE installed, main menu constructed, and app remained alive for 15 seconds."
adb shell dumpsys activity activities | grep -E 'mResumedActivity|ResumedActivity' || true
