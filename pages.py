"""The Package: multi-page build + zip delivery. The full $20k scroll set."""
import re
import shutil
import zipfile
from pathlib import Path

PAGES = ["about", "services", "contact"]

def extract_css(html):
    """Steal the home page's style block so every page shares one system."""
    m = re.search(r"<style.*?</style>", html, re.S)
    return m.group(0) if m else ""

def build_pages(order, home_html, summon_fn):
    """Forge the sub-pages from the home page's exact CSS. Returns {name: html}."""
    css = extract_css(home_html)
    pages = {"index": home_html}
    for name in PAGES:
        print(f"📄 Forging the {name} page")
        brief = (
            f"{order}\n\nBuild the {name.upper()} page of this same website. "
            "Reuse EXACTLY this CSS block (same classes, do not restyle) and the same "
            "header nav and footer as the home page. Nav links: index.html (Home), "
            "about.html, services.html, contact.html.\n\n"
            f"{css}\n\n"
            f"Write content appropriate for a {name} page of this brand, same voice, "
            "same images available. Output ONLY the complete HTML document."
        )
        pages[name] = summon_fn(brief)
    return pages

def package(pages, kit_html=""):
    """Bundle pages + kit + painted assets into static/forge-package.zip."""
    pkg = Path("package")
    shutil.rmtree(pkg, ignore_errors=True)
    (pkg / "assets").mkdir(parents=True)
    for img in Path("static").glob("*.png"):
        shutil.copy(img, pkg / "assets" / img.name)
    if kit_html:
        (pkg / "brand-kit.html").write_text(kit_html)
    for name, html in pages.items():
        html = html.replace('src="/static/', 'src="assets/')
        html = html.replace(" — ", ", ").replace("—", "-")
        (pkg / f"{name}.html").write_text(html)
    zip_path = Path("static/forge-package.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(pkg.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(pkg))
    return str(zip_path)
