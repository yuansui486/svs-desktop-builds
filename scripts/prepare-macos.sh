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
