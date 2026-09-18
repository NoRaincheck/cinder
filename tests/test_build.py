import subprocess
from pathlib import Path

# Toolchain channel: official Tweego 2.1.1 release binary (GitHub) + Chapbook
# 2.3.0 story format (klembot.github.io), bootstrapped by tools/setup-tweego.sh.
# The `npx tweego@2.1.1` channel is dead (npm registry 404) — see task-5 report.
TWEEGO = Path("build/tweego/tweego")


def test_tweego_builds_all_four_stories_and_landing():
    setup = subprocess.run(["tools/setup-tweego.sh"],
                           capture_output=True, text=True, timeout=300)
    assert setup.returncode == 0, setup.stderr[-2000:]
    assert TWEEGO.exists(), "tweego binary missing after setup"
    Path("dist").mkdir(parents=True, exist_ok=True)
    for src, out in [("src/glass", "dist/glass.html"),
                     ("src/bronze", "dist/bronze.html"),
                     ("src/indigo", "dist/indigo.html"),
                     ("src/alabaster", "dist/alabaster.html")]:
        r = subprocess.run([str(TWEEGO), src, "-o", out],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-2000:]
        p = subprocess.run(["node", "tools/patch-chapbook.js", out],
                           capture_output=True, text=True, timeout=60)
        assert p.returncode == 0, p.stderr[-2000:]
    r = subprocess.run(["python3", "tools/build-landing.py"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-2000:]

    glass = Path("dist/glass.html")
    assert glass.exists() and glass.stat().st_size > 50_000
    gtext = glass.read_text(errors="replace")
    # Canonical Glass endings (glass.ni): Cinderella-wed/peace,
    # Cinderella-executed/disaster, Lucinda-Marriage (+ Prince-Departs,
    # Theodora-Marriage asserted via link integrity/reachability).
    assert "Glass" in gtext
    assert "Start" in gtext
    for end in ["End-Cinderella-Wed", "End-Lucinda-Marriage", "End-Cinderella-Executed"]:
        assert end in gtext, f"ending missing from glass build: {end}"

    bronze = Path("dist/bronze.html")
    assert bronze.exists() and bronze.stat().st_size > 50_000
    btext = bronze.read_text(errors="replace")
    assert "Bronze" in btext
    assert "Bronze-Start" in btext
    assert "End-Bronze-Leave" in btext

    indigo = Path("dist/indigo.html")
    assert indigo.exists() and indigo.stat().st_size > 50_000
    itext = indigo.read_text(errors="replace")
    assert "Indigo" in itext
    assert "Indigo-Start" in itext
    assert "End-Indigo-Escape" in itext

    alabaster = Path("dist/alabaster.html")
    assert alabaster.exists() and alabaster.stat().st_size > 50_000
    atext = alabaster.read_text(errors="replace")
    assert "Alabaster" in atext
    assert "Alabaster-Start" in atext
    assert "End-Alabaster-Sundering" in atext

    landing = Path("dist/index.html").read_text(errors="replace")
    assert 'href="glass.html"' in landing
    assert 'href="bronze.html"' in landing
    assert 'href="indigo.html"' in landing
    assert 'href="alabaster.html"' in landing

    # Scene art: every generated asset must exist in src/ and survive
    # Tweego compilation into the built HTML (imported as Twine.image
    # passages; src strings retained in the output).
    glass_art = [
        "glass-prologue.webp",
        "glass-wondering-ball.webp",
        "glass-fitting.webp",
        "glass-checking.webp",
        "glass-cinderella.webp",
        "glass-ending.webp",
    ]
    bronze_art = [
        "bronze-gate.webp",
        "bronze-courtyard.webp",
        "bronze-scarlet.webp",
        "bronze-beast.webp",
        "bronze-library.webp",
        "bronze-rotunda.webp",
        "bronze-crypt.webp",
    ]
    indigo_art = [
        "indigo-kitchen.webp",
        "indigo-cauldron.webp",
        "indigo-tower.webp",
        "indigo-hair.webp",
        "indigo-candle.webp",
        "indigo-storeroom.webp",
        "indigo-escape.webp",
    ]
    for name in glass_art:
        assert (Path("src/glass/assets") / name).exists(), f"missing src art: {name}"
        assert f"assets/glass/{name}" in gtext, f"art missing from glass build: {name}"
    for name in bronze_art:
        assert (Path("src/bronze/assets") / name).exists(), f"missing src art: {name}"
        assert f"assets/bronze/{name}" in btext, f"art missing from bronze build: {name}"
    for name in indigo_art:
        assert (Path("src/indigo/assets") / name).exists(), f"missing src art: {name}"
        assert f"assets/indigo/{name}" in itext, f"art missing from indigo build: {name}"
    alabaster_art = [
        "alabaster-woods.webp",
        "alabaster-snow.webp",
        "alabaster-box.webp",
        "alabaster-hart.webp",
        "alabaster-possession.webp",
        "alabaster-exorcism.webp",
        "alabaster-haven.webp",
        "alabaster-reunion.webp",
    ]
    for name in alabaster_art:
        assert (Path("src/alabaster/assets") / name).exists(), f"missing src art: {name}"
        assert f"assets/alabaster/{name}" in atext, f"art missing from alabaster build: {name}"
