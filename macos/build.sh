#!/usr/bin/env bash
# Build a macOS .app bundle with Nuitka and package it into a .dmg.
# Produces dist/GFN Discord RPC.app and dist/GFN-Discord-RPC-<arch>.dmg.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ASSETS="$ROOT/assets"
DIST="$ROOT/dist"
BUILD="$ROOT/build/nuitka"
APP_NAME="GFN Discord RPC"
BUNDLE_ID="com.lumidevlabs.gfndiscordrpc"
APP_BUNDLE="$DIST/$APP_NAME.app"
ARCH="$(uname -m)"
DMG_PATH="$DIST/GFN-Discord-RPC-$ARCH.dmg"

PNG_ICON="$ASSETS/app.png"
ICNS_ICON="$ASSETS/app.icns"

cd "$ROOT"

if [[ ! -f "$PNG_ICON" ]]; then
    echo "Missing assets/app.png - place your icon there before building." >&2
    exit 1
fi

# --- install dependencies via uv ---
uv python pin 3.13
uv sync
uv pip install nuitka
# PyObjC frameworks needed for tray (pystray darwin backend) and window detection.
uv pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz

PYTHON="$(uv run python -c 'import sys; print(sys.executable)')"

# --- generate .icns from the PNG if not committed ---
if [[ ! -f "$ICNS_ICON" ]]; then
    echo "Generating app.icns from app.png..."
    ICONSET="$(mktemp -d)/app.iconset"
    mkdir -p "$ICONSET"
    for size in 16 32 64 128 256 512; do
        sips -z "$size" "$size" "$PNG_ICON" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
        double=$((size * 2))
        sips -z "$double" "$double" "$PNG_ICON" --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
    done
    iconutil -c icns "$ICONSET" -o "$ICNS_ICON"
fi

mkdir -p "$DIST"
rm -rf "$APP_BUNDLE"

# --- compile with Nuitka into an .app bundle ---
# --macos-app-mode=ui-element => menu-bar agent with no Dock icon (LSUIElement).
"$PYTHON" -m nuitka \
    --standalone \
    --assume-yes-for-downloads \
    --macos-create-app-bundle \
    --macos-app-icon="$ICNS_ICON" \
    --macos-app-mode=ui-element \
    --macos-app-name="$APP_NAME" \
    --include-package=shared \
    --include-package=macos \
    --include-package=pystray \
    --include-module=Quartz \
    --include-data-files="$PNG_ICON=assets/app.png" \
    --output-dir="$BUILD" \
    --output-filename="$APP_NAME" \
    "$ROOT/main.py"

# Nuitka emits "<output-filename>.app" in the build dir.
BUILT_APP="$BUILD/$APP_NAME.app"
if [[ ! -d "$BUILT_APP" ]]; then
    # Fall back to the default "main.app" name if needed.
    BUILT_APP="$BUILD/main.app"
fi
cp -R "$BUILT_APP" "$APP_BUNDLE"
echo "Built: $APP_BUNDLE"

# --- ad-hoc code signing ---
# Sign with the ad-hoc identity ("-"): no Apple account or certificate required.
# On Apple Silicon every binary must carry a valid signature to execute at all,
# so we re-sign the finished bundle (including the dylibs Nuitka bundles) to make
# sure copying/packaging didn't invalidate anything.  Pinning the bundle
# identifier keeps the code identity consistent.  This does NOT bypass Gatekeeper
# (users still "Open Anyway" once) and is no substitute for Developer ID
# notarization, which is the only thing that fully removes the first-launch
# warning and reliably preserves TCC permissions across updates.
codesign --force --deep --sign - --identifier "$BUNDLE_ID" "$APP_BUNDLE"
codesign --verify --verbose=2 "$APP_BUNDLE" || echo "warning: codesign verification reported issues" >&2

# --- package into a .dmg ---
rm -f "$DMG_PATH"
if command -v create-dmg >/dev/null 2>&1; then
    STAGING="$(mktemp -d)"
    cp -R "$APP_BUNDLE" "$STAGING/"
    create-dmg \
        --volname "$APP_NAME" \
        --app-drop-link 450 150 \
        --icon "$APP_NAME.app" 150 150 \
        --window-size 600 320 \
        "$DMG_PATH" "$STAGING" || true
fi

# Fallback (or if create-dmg is unavailable): build with hdiutil + Applications link.
if [[ ! -f "$DMG_PATH" ]]; then
    STAGING="$(mktemp -d)"
    cp -R "$APP_BUNDLE" "$STAGING/"
    ln -s /Applications "$STAGING/Applications"
    hdiutil create \
        -volname "$APP_NAME" \
        -srcfolder "$STAGING" \
        -ov -format UDZO \
        "$DMG_PATH"
fi

echo "Built: $DMG_PATH"
