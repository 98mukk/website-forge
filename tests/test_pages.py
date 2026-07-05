"""The Package forge: CSS extraction, the em-dash ban, and zip delivery."""
import zipfile

from pages import extract_css, package

def test_extract_css_pulls_style_block():
    html = "<html><head><style>\nbody { color: #C9A227; }\n</style></head><body></body></html>"
    css = extract_css(html)
    assert css.startswith("<style")
    assert css.endswith("</style>")
    assert "#C9A227" in css

def test_extract_css_no_style():
    assert extract_css("<html><body>bare</body></html>") == ""

def sanitize(text):
    """The contract sanitizer: ' — ' becomes ', ' then any leftover '—' becomes '-'."""
    return text.replace(" — ", ", ").replace("—", "-")

def test_emdash_sanitizer():
    assert sanitize("bold — clean") == "bold, clean"
    assert sanitize("mid—word") == "mid-word"
    assert "—" not in sanitize("a — b—c — d")

def test_package_zips_correctly(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)                        # package() uses relative paths
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "hero.png").write_bytes(b"not-a-real-png")
    fake_pages = {
        "index": '<html><img src="/static/hero.png"> Craft — done right, mid—word.</html>',
        "about": "<html>the about page</html>",
    }
    zip_path = package(fake_pages, kit_html="<html>the kit</html>")
    assert zip_path == "static/forge-package.zip"
    with zipfile.ZipFile(tmp_path / zip_path) as z:
        names = set(z.namelist())
        assert {"index.html", "about.html", "brand-kit.html", "assets/hero.png"} <= names
        index = z.read("index.html").decode()
    assert 'src="assets/hero.png"' in index            # image paths rewritten for the zip
    assert "—" not in index                            # em-dash ban enforced
    assert "Craft, done right" in index
