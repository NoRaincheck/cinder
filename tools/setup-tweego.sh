#!/bin/sh
# Install the pinned Tweego + Chapbook toolchain into build/tweego/.
# Idempotent: skips downloads that are already in place and version-correct.
#
# Why not npm: the `tweego` package does not exist on the npm registry (404),
# and the `chapbook` npm package is an unrelated CSS project (latest 1.2.2) —
# the Chapbook story format was published as `Chapbook` (capital C), which the
# modern registry rejects. So both pins are sourced from their official homes:
#   Tweego 2.1.1 binary ... https://github.com/tmedwards/tweego/releases
#   Chapbook 2.3.0 format .. https://klembot.github.io/chapbook/use/2.3.0/
# The version strings in package.json devDependencies mirror these pins.
set -eu

TWEEGO_VERSION="2.1.1"
CHAPBOOK_VERSION="2.3.0"
DEST="build/tweego"
BIN="$DEST/tweego"
FORMAT_DIR="$DEST/storyformats/chapbook-2"

need_download=1
if [ -x "$BIN" ]; then
	# NB: tweego prints --version to stderr.
	if "$BIN" --version 2>&1 | grep -q "version $TWEEGO_VERSION"; then
		need_download=0
	fi
fi

need_format=1
if [ -f "$FORMAT_DIR/format.js" ]; then
	if grep -q "\"version\":\"$CHAPBOOK_VERSION\"" "$FORMAT_DIR/format.js"; then
		need_format=0
	fi
fi

if [ "$need_download" = 0 ] && [ "$need_format" = 0 ]; then
	echo "toolchain already installed (tweego $TWEEGO_VERSION, chapbook $CHAPBOOK_VERSION)"
	exit 0
fi

OS="$(uname -s)"
ARCH="$(uname -m)"
case "$OS-$ARCH" in
	Darwin-x86_64|Darwin-arm64) ASSET="tweego-$TWEEGO_VERSION-macos-x64.zip" ;;
	Linux-x86_64) ASSET="tweego-$TWEEGO_VERSION-linux-x64.zip" ;;
	Linux-i686|Linux-i386) ASSET="tweego-$TWEEGO_VERSION-linux-x86.zip" ;;
	*) echo "unsupported platform: $OS-$ARCH" >&2; exit 1 ;;
esac
# Note: no macos-arm64 asset exists for 2.1.1 (2020-era release); the x64
# binary runs on Apple Silicon via Rosetta 2.

if [ "$need_download" = 1 ]; then
	TMP="$(mktemp -d)"
	trap 'rm -rf "$TMP"' EXIT INT TERM
	URL="https://github.com/tmedwards/tweego/releases/download/v$TWEEGO_VERSION/$ASSET"
	echo "downloading $URL"
	if command -v curl >/dev/null 2>&1; then
		curl -sSL -o "$TMP/tweego.zip" "$URL"
	else
		wget -O "$TMP/tweego.zip" "$URL"
	fi
	mkdir -p "$DEST"
	unzip -o -q "$TMP/tweego.zip" -d "$DEST"
	chmod +x "$BIN"
	rm -rf "$TMP"
	trap - EXIT INT TERM
fi

if [ "$need_format" = 1 ]; then
	mkdir -p "$FORMAT_DIR"
	BASE="https://klembot.github.io/chapbook/use/$CHAPBOOK_VERSION"
	echo "downloading $BASE/format.js"
	if command -v curl >/dev/null 2>&1; then
		curl -sSL -o "$FORMAT_DIR/format.js" "$BASE/format.js"
	else
		wget -O "$FORMAT_DIR/format.js" "$BASE/format.js"
	fi
	# Logo is cosmetic (Twine library icon); best effort only.
	curl -sSL -o "$FORMAT_DIR/logo.svg" "$BASE/logo.svg" 2>/dev/null || true
fi

echo "installed: $("$BIN" --version 2>&1 | grep -o "version [^ ]*"), chapbook $CHAPBOOK_VERSION"
