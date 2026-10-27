#!/usr/bin/env bash
set -euo pipefail
cd "$1"
test "$(uname -m)" = arm64
rustup toolchain install stable --profile minimal
rustup default stable
rustup target add aarch64-apple-darwin
node --version
cargo --version
npm --prefix crates/svs-gui/frontend ci --no-audit --no-fund
npm --prefix crates/svs-remotion-assets/vendor/remotion-runtime ci --ignore-scripts --no-audit --no-fund
(
  cd crates/svs-remotion-assets/vendor/remotion-runtime
  node node_modules/@remotion/cli/remotion-cli.js browser ensure
)
mkdir -p vendor/packaging/media-tools/mac-arm64
cd vendor/packaging/media-tools/mac-arm64
curl --fail --location --retry 3 -o ffmpeg https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-darwin-arm64
curl --fail --location --retry 3 -o ffprobe https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffprobe-darwin-arm64
echo 'a90e3db6a3fd35f6074b013f948b1aa45b31c6375489d39e572bea3f18336584  ffmpeg' | shasum -a 256 -c -
echo 'bb2db6f5d8cef919da12fbf592119a987202a8c060a886f3cab091f9cab90b64  ffprobe' | shasum -a 256 -c -
chmod +x ffmpeg ffprobe
./ffmpeg -version
./ffprobe -version
otool -L ffmpeg
otool -L ffprobe
