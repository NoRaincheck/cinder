import json
import tomllib
from pathlib import Path


def test_package_pins_tweego_chapbook():
    pkg = json.loads(Path("package.json").read_text())
    assert pkg["devDependencies"]["tweego"] == "2.1.1"
    assert pkg["devDependencies"]["chapbook"] == "2.3.0"


def test_pyproject_pins_pytest():
    proj = tomllib.loads(Path("pyproject.toml").read_text())
    dev = proj["dependency-groups"]["dev"]
    assert "pytest>=9.1.1" in dev


def test_pages_workflow_exists():
    wf = Path(".github/workflows/pages.yml").read_text()
    assert "tweego" in wf and "deploy-pages" in wf


def test_justfile_has_recipes():
    jf = Path("justfile").read_text()
    for recipe in ["setup:", "build:", "test:", "preview:", "fmt:"]:
        assert recipe in jf, f"justfile missing recipe {recipe}"
    # extract is parameterized: `just extract` (all), `just extract glass|bronze`.
    assert 'extract story="all":' in jf, "justfile missing parameterized extract recipe"
    assert "build/tweego/tweego" in jf
    assert "http.server" in jf
