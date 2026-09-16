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

# Generate dist/index.html landing linking both stories.
build-landing:
    python3 tools/build-landing.py
    ls -la dist

# Compile both stories + landing to dist/.
build: setup
    mkdir -p dist dist/assets/glass dist/assets/bronze
    cp -n src/glass/assets/*.png dist/assets/glass/ 2>/dev/null || cp src/glass/assets/*.png dist/assets/glass/
    cp -n src/bronze/assets/*.png dist/assets/bronze/ 2>/dev/null || cp src/bronze/assets/*.png dist/assets/bronze/
    {{tweego}} src/glass -o dist/glass.html
    node tools/patch-chapbook.js dist/glass.html
    {{tweego}} src/bronze -o dist/bronze.html
    node tools/patch-chapbook.js dist/bronze.html
    python3 tools/build-landing.py
    ls -la dist dist/assets/glass dist/assets/bronze

# Run the full pytest suite (coverage, links, reachability, build, polish).
test:
    python3 -m pytest tests/ -v

# Re-extract graphs: `just extract` (all), `just extract glass`, `just extract bronze`.
extract story="all":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "{{story}}" != "glass" ] && [ "{{story}}" != "bronze" ] && [ "{{story}}" != "all" ]; then
        echo "unknown story: {{story}} (glass|bronze|all)" >&2
        exit 1
    fi
    if [ "{{story}}" = "glass" ] || [ "{{story}}" = "all" ]; then
        if [ -f ref/source/glass.ni ]; then
            SRC=ref/source/glass.ni
        else
            echo "ref/source/glass.ni missing; fetching snapshot" >&2
            curl -sSL https://raw.githubusercontent.com/I7-Examples/Glass/main/Glass.inform/Source/story.ni -o ref/source/glass.ni
            SRC=ref/source/glass.ni
        fi
        python3 tools/extract.py "$SRC" data
        cat data/extraction-report.json
    fi
    if [ "{{story}}" = "bronze" ] || [ "{{story}}" = "all" ]; then
        if [ ! -f ref/source/bronze.ni ]; then
            echo "ref/source/bronze.ni missing; fetching snapshot" >&2
            curl -sSL https://raw.githubusercontent.com/I7-Examples/Bronze/main/Bronze.inform/Source/story.ni -o ref/source/bronze.ni
        fi
        python3 tools/extract.py ref/source/bronze.ni data --story bronze
        cat data/bronze-extraction-report.json
    fi

# Build, then serve dist/ locally so you can play the game in a browser.
preview: build
    @echo "Playing Twee-Glass at http://localhost:{{port}} (Ctrl-C to stop)..."
    python3 -m http.server {{port}} --directory dist

# Remove build outputs and caches.
clean:
    rm -rf dist build .pytest_cache
    find . -name "__pycache__" -type d -prune -exec rm -rf {} +

# Format story sources: append two spaces after any line ending in ]] (Chapbook link rule).
fmt:
    @sed -i '' -E 's/\]\][ ]?$/]]  /' src/glass/glass.twee src/bronze/bronze.twee

# Compile Glass story dir to dist/glass.html.
build-glass: setup
    mkdir -p dist dist/assets/glass
    cp -n src/glass/assets/*.png dist/assets/glass/ 2>/dev/null || cp src/glass/assets/*.png dist/assets/glass/
    {{tweego}} src/glass -o dist/glass.html
    node tools/patch-chapbook.js dist/glass.html

# Compile Bronze story dir to dist/bronze.html.
build-bronze: setup
    mkdir -p dist dist/assets/bronze
    cp -n src/bronze/assets/*.png dist/assets/bronze/ 2>/dev/null || cp src/bronze/assets/*.png dist/assets/bronze/
    {{tweego}} src/bronze -o dist/bronze.html
    node tools/patch-chapbook.js dist/bronze.html
