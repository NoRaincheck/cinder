# Twee-Glass task runner. Run `just` (no args) to list recipes.
# Prereqs: just (https://just.systems), python3. The Tweego binary and
# Chapbook format are fetched by `just setup` — nothing to install by hand.

tweego := "build/tweego/tweego"
port := "8765"

# List available recipes.
default:
    @just --list

# Install pinned test deps + Tweego 2.1.1 / Chapbook 2.3.0 toolchain.
setup:
    pip3 install -r requirements.txt
    tools/setup-tweego.sh

# Compile src/*.twee (Chapbook) to dist/index.html.
build: setup
    mkdir -p dist
    {{tweego}} src -o dist/index.html
    ls -la dist

# Run the full pytest suite (coverage, links, reachability, build, polish).
test:
    python3 -m pytest tests/ -v

# Re-extract graph.json + prune-list.json from the Inform 7 source.
extract:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f vendor/glass/Glass.inform/Source/story.ni ]; then
        SRC=vendor/glass/Glass.inform/Source/story.ni
    elif [ -f data/story.ni ]; then
        SRC=data/story.ni
    else
        echo "submodule not initialized; fetching snapshot" >&2
        curl -sSL https://raw.githubusercontent.com/I7-Examples/Glass/main/Glass.inform/Source/story.ni -o data/story.ni
        SRC=data/story.ni
    fi
    if [ "$SRC" != "data/story.ni" ]; then cp "$SRC" data/story.ni; fi
    python3 tools/extract.py data/story.ni data
    cat data/extraction-report.json

# Build, then serve dist/ locally so you can play the game in a browser.
preview: build
    @echo "Playing Twee-Glass at http://localhost:{{port}} (Ctrl-C to stop)..."
    python3 -m http.server {{port}} --directory dist

# Format src/glass.twee: append two spaces after any line ending in ]] (Chapbook link rule).
fmt:
	@sed -i '' -E 's/\]\][ ]?$/]]  /' src/glass.twee
