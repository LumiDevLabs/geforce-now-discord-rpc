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

# --- code signing ---
# macOS TCC permissions (Screen Recording) are tied to the app's code-signing
# identity - specifically its cdhash.  The ad-hoc identity ("-") hashes the
# binary bytes, so every new build produces a new identity and silently breaks
# any existing Screen Recording grant for users who already installed the app.
#
# The fix: sign every build with the *same* persistent certificate so the
# identity is stable across releases.  Priority order:
#
#  1. CI (GitHub Actions): CODESIGN_CERT_P12_BASE64 + CODESIGN_CERT_PASSWORD
#     secrets → imported into a temp keychain each run.  Generate the p12 once
#     locally (see README) and store it as a repository secret.
#
#  2. Local dev: a persistent self-signed cert in ~/.gfn-discord-rpc-signing/,
#     generated once on first build and reused forever.
#
#  3. Fallback: ad-hoc ("-") if neither is available.  TCC will break on every
#     build in this case; avoid if at all possible.

SIGN_IDENTITY=""
SIGN_KEYCHAIN_ARGS=()
_TEMP_KEYCHAIN=""

_cleanup_temp_keychain() {
    if [[ -n "$_TEMP_KEYCHAIN" && -f "$_TEMP_KEYCHAIN" ]]; then
        security delete-keychain "$_TEMP_KEYCHAIN" 2>/dev/null || true
    fi
}
trap _cleanup_temp_keychain EXIT

# --- path 1: CI secrets ---
if [[ -n "${CODESIGN_CERT_P12_BASE64:-}" && -n "${CODESIGN_CERT_PASSWORD:-}" ]]; then
    echo "Importing signing identity from CI secrets..."
    _TEMP_KEYCHAIN="$(mktemp).keychain-db"
    _TMP_P12="$(mktemp).p12"
    printf '%s' "$CODESIGN_CERT_P12_BASE64" | base64 --decode > "$_TMP_P12"

    security create-keychain -p "ci-temp" "$_TEMP_KEYCHAIN"
    security set-keychain-settings "$_TEMP_KEYCHAIN"   # disable auto-lock
    security unlock-keychain -p "ci-temp" "$_TEMP_KEYCHAIN"
    security import "$_TMP_P12" -k "$_TEMP_KEYCHAIN" \
        -P "$CODESIGN_CERT_PASSWORD" -T /usr/bin/codesign -A
    security set-key-partition-list -S apple-tool:,apple:,codesign: \
        -s -k "ci-temp" "$_TEMP_KEYCHAIN" >/dev/null 2>&1 || true
    rm -f "$_TMP_P12"

    # Add to search list so codesign can find the identity by name.
    _existing_keychains="$(security list-keychains -d user | sed -e 's/^[[:space:]]*//' -e 's/"//g')"
    security list-keychains -d user -s "$_TEMP_KEYCHAIN" $_existing_keychains || true

    SIGN_IDENTITY="$(security find-identity -v -p codesigning "$_TEMP_KEYCHAIN" \
        | awk -F'"' 'NR==1{print $2}')"
    SIGN_KEYCHAIN_ARGS=(--keychain "$_TEMP_KEYCHAIN")
fi

# --- path 2: local persistent self-signed cert ---
if [[ -z "$SIGN_IDENTITY" ]]; then
    _SIGN_DIR="$HOME/.gfn-discord-rpc-signing"
    _LOCAL_KEYCHAIN="$_SIGN_DIR/signing.keychain-db"
    _LOCAL_P12="$_SIGN_DIR/identity.p12"
    _LOCAL_CN="GFN Discord RPC"
    _LOCAL_KW="gfn-discord-rpc"

    _setup_local_cert() {
        mkdir -p "$_SIGN_DIR"

        if [[ ! -f "$_LOCAL_P12" ]]; then
            echo "Creating persistent local signing identity (one-time setup)..."
            local tmp; tmp="$(mktemp -d)"
            cat > "$tmp/openssl.cnf" <<EOF
[ req ]
distinguished_name = dn
x509_extensions = v3
prompt = no
[ dn ]
CN = $_LOCAL_CN
[ v3 ]
basicConstraints = critical,CA:false
keyUsage = critical,digitalSignature
extendedKeyUsage = critical,codeSigning
EOF
            openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
                -keyout "$tmp/key.pem" -out "$tmp/cert.pem" -config "$tmp/openssl.cnf"
            openssl pkcs12 -export -inkey "$tmp/key.pem" -in "$tmp/cert.pem" \
                -name "$_LOCAL_CN" -out "$_LOCAL_P12" -passout "pass:$_LOCAL_KW"
            rm -rf "$tmp"
        fi

        if [[ ! -f "$_LOCAL_KEYCHAIN" ]]; then
            security create-keychain -p "$_LOCAL_KW" "$_LOCAL_KEYCHAIN"
        fi
        security set-keychain-settings "$_LOCAL_KEYCHAIN"
        security unlock-keychain -p "$_LOCAL_KW" "$_LOCAL_KEYCHAIN"

        if ! security find-identity -v -p codesigning "$_LOCAL_KEYCHAIN" | grep -qF "$_LOCAL_CN"; then
            security import "$_LOCAL_P12" -k "$_LOCAL_KEYCHAIN" \
                -P "$_LOCAL_KW" -T /usr/bin/codesign -A
            security set-key-partition-list -S apple-tool:,apple:,codesign: \
                -s -k "$_LOCAL_KW" "$_LOCAL_KEYCHAIN" >/dev/null 2>&1 || true
        fi

        local existing
        existing="$(security list-keychains -d user | sed -e 's/^[[:space:]]*//' -e 's/"//g')"
        if ! printf '%s\n' "$existing" | grep -qF "$_LOCAL_KEYCHAIN"; then
            security list-keychains -d user -s "$_LOCAL_KEYCHAIN" $existing || true
        fi
    }

    _setup_local_cert || true
    if security find-identity -v -p codesigning "$_LOCAL_KEYCHAIN" 2>/dev/null | grep -qF "$_LOCAL_CN"; then
        SIGN_IDENTITY="$_LOCAL_CN"
        SIGN_KEYCHAIN_ARGS=(--keychain "$_LOCAL_KEYCHAIN")
    fi
fi

# --- path 3: ad-hoc fallback ---
if [[ -z "$SIGN_IDENTITY" ]]; then
    echo "warning: no persistent signing identity found - falling back to ad-hoc signing." >&2
    echo "warning: Screen Recording permission will break for users on every update." >&2
    SIGN_IDENTITY="-"
fi

echo "Signing with identity: $SIGN_IDENTITY"
codesign --force --deep --sign "$SIGN_IDENTITY" \
    ${SIGN_KEYCHAIN_ARGS[@]+"${SIGN_KEYCHAIN_ARGS[@]}"} \
    --identifier "$BUNDLE_ID" "$APP_BUNDLE"
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
