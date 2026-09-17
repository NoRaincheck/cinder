from pathlib import Path


def test_landing_links_all_three_stories():
    html = Path("dist/index.html").read_text(errors="replace")
    assert 'href="glass.html"' in html
    assert 'href="bronze.html"' in html
    assert 'href="indigo.html"' in html
    assert "Glass" in html and "Bronze" in html
    assert "Indigo" in html
    assert "fractured fairy tale" in html
