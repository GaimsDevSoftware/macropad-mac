#!/bin/bash
# Bygg Makropad.app og Makropad.dmg — selvstendig, med Python innebygd.
#
#   ./build.sh
#
# Resultat: dist/Makropad.dmg
set -euo pipefail
cd "$(dirname "$0")"

APP="Makropad"
VENV=".venv"
PY="$VENV/bin/python"

echo "▸ Avhengigheter"
[ -d "$VENV" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q -r requirements.txt pyinstaller rumps

echo "▸ Ikoner"
if [ ! -f build_assets/Makropad.icns ]; then
  if "$PY" -c "import cairosvg" 2>/dev/null; then
    (cd design && "../$PY" render_icons.py >/dev/null)
  fi
  if [ -d build_assets/Makropad.iconset ]; then
    rm -f build_assets/Makropad.iconset/icon_64x64*.png \
          build_assets/Makropad.iconset/icon_1024x1024.png
    iconutil -c icns build_assets/Makropad.iconset -o build_assets/Makropad.icns
  else
    echo "  (ingen ikoner — bygger uten. Kjør design/render_icons.py med cairosvg installert.)"
  fi
fi

echo "▸ Rydder"
rm -rf build dist "$APP.spec"

echo "▸ PyInstaller"
ICON_ARG=()
[ -f build_assets/Makropad.icns ] && ICON_ARG=(--icon build_assets/Makropad.icns)
MB_ARG=()
[ -f build_assets/MenubarIconTemplate.png ] && \
  MB_ARG=(--add-data "build_assets/MenubarIconTemplate.png:." \
          --add-data "build_assets/MenubarIconTemplate@2x.png:.")

"$VENV/bin/pyinstaller" \
  --name "$APP" \
  --windowed \
  --noconfirm \
  --clean \
  --log-level WARN \
  "${ICON_ARG[@]}" \
  "${MB_ARG[@]}" \
  --add-data "ui.html:." \
  --hidden-import paths \
  --hidden-import access \
  --add-data "profiles.example.yaml:." \
  --osx-bundle-identifier no.macropad.app \
  --hidden-import hid \
  --hidden-import yaml \
  --hidden-import rumps \
  --hidden-import Quartz \
  --hidden-import AppKit \
  --collect-submodules objc \
  --collect-all rumps \
  menubar.py

PLIST="dist/$APP.app/Contents/Info.plist"
echo "▸ Info.plist"
/usr/libexec/PlistBuddy -c "Set :LSUIElement true" "$PLIST" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$PLIST"
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString 1.0" "$PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :NSHumanReadableCopyright string 'MIT'" "$PLIST" 2>/dev/null || true

echo "▸ Signerer lokalt (ad-hoc)"
codesign --force --deep --sign - "dist/$APP.app" 2>/dev/null || \
  echo "  (codesign hoppet over)"

echo "▸ DMG"
STAGE=$(mktemp -d)
cp -R "dist/$APP.app" "$STAGE/"
ln -s /Applications "$STAGE/Programmer"
cat > "$STAGE/Les meg.txt" <<'EOF'
Makropad — konfigurator for XZKJ 12-key/4-knob makropad

1. Dra Makropad til Programmer.
2. Start den. Første gang: høyreklikk → Åpne (appen er ikke signert av Apple).
3. Gi Tilgjengelighet-tilgang når den spør — appen må lese padden for å
   oversette tastene.
4. Velg «Klargjør padden» i menylinja. Én gang, så er du i gang.

https://github.com/GaimsDevSoftware/macropad-mac
EOF
rm -f "dist/$APP.dmg"
hdiutil create -volname "$APP" -srcfolder "$STAGE" -ov -format UDZO \
  -quiet "dist/$APP.dmg"
rm -rf "$STAGE"

echo
echo "✓ dist/$APP.app"
echo "✓ dist/$APP.dmg   ($(du -h "dist/$APP.dmg" | cut -f1))"
