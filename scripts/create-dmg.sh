#!/usr/bin/env bash
set -euo pipefail
delivery="$1"
image_root=$(mktemp -d "${RUNNER_TEMP}/svs-dmg.XXXXXX")
ditto -x -k "$delivery/svs-app-mac-arm64-lite.zip" "$image_root"
test -d "$image_root/新媒体后台.app/Contents/MacOS"
test "$(find "$image_root" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')" = 1
ln -s /Applications "$image_root/Applications"
hdiutil create -volname 'SVS 新媒体后台' -srcfolder "$image_root" -ov -format UDZO "$delivery/svs-app-mac-arm64.dmg"
cd "$delivery"
shasum -a 256 svs-app-mac-arm64-lite.zip svs-app-mac-arm64-offline.zip svs-app-mac-arm64.dmg > SHA256SUMS.txt
