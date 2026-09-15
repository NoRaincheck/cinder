import json
from pathlib import Path


def test_package_pins_tweego_chapbook():
    pkg = json.loads(Path("package.json").read_text())
    assert pkg["devDependencies"]["tweego"] == "2.1.1"
    assert pkg["devDependencies"]["chapbook"] == "2.3.0"


def test_requirements_pins_pytest():
    req = Path("requirements.txt").read_text()
    assert "pytest==8.3" in req


def test_pages_workflow_exists():
    wf = Path(".github/workflows/pages.yml").read_text()
    assert "tweego" in wf and "deploy-pages" in wf
