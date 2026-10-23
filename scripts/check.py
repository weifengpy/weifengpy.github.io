#!/usr/bin/env python3
"""SEO gate for the built site (plan section 5, gates G1-G3).

Scans the Hugo output directory and fails (exit 1) if any check fails:
  - every HTML page has a non-empty meta description, unique site-wide
  - every page's canonical link points at its own URL (self-referential)
  - every <img> has a non-empty alt and width+height attributes
  - every JSON-LD block parses as JSON; home page and posts must have one
  - sitemap.xml exists and lists every public page (except 404)
Usage: python3 scripts/check.py [public_dir]   (default: public)
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "https://weifengpy.github.io"

# Redirect pages: built path -> the canonical target the page must point at.
# /about/ exists only to redirect to the front page, which now carries the
# About content (GitHub Pages has no server-side 301), so it is exempt from
# exactly two rules: self-referential canonical and sitemap coverage (and it
# must NOT appear in the sitemap).
# Every other check below still applies to it in full.
REDIRECTS = {"about/index.html": f"{BASE}/"}
pub = Path(sys.argv[1] if len(sys.argv) > 1 else "public")
errors = []
warnings = []

html_files = sorted(pub.rglob("*.html"))
if not html_files:
    print("FAIL: no HTML files found under", pub)
    sys.exit(1)

def url_for(path: Path) -> str:
    rel = path.relative_to(pub).as_posix()
    if rel == "index.html":
        return f"{BASE}/"
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    return f"{BASE}/{rel}"

descriptions = {}
jsonld_pages = set()
for f in html_files:
    text = f.read_text(encoding="utf-8")
    url = url_for(f)
    rel = f.relative_to(pub).as_posix()

    # note: hugo --minify strips attribute quotes where legal, so quotes are optional below
    m = re.search(r'<meta\s+name="?description"?\s+content="([^"]*)"', text)
    if not m or not m.group(1).strip():
        errors.append(f"{rel}: missing or empty meta description")
    else:
        d = m.group(1).strip()
        if d in descriptions:
            errors.append(f"{rel}: duplicate description also used by {descriptions[d]}")
        descriptions[d] = rel

    m = re.search(r'<link\s+rel="?canonical"?\s+href="?([^"\s>]+)"?', text)
    if not m:
        errors.append(f"{rel}: missing canonical link")
    elif rel in REDIRECTS:
        if m.group(1) != REDIRECTS[rel]:
            errors.append(f"{rel}: redirect canonical {m.group(1)} != target {REDIRECTS[rel]}")
    elif m.group(1) != url:
        errors.append(f"{rel}: canonical {m.group(1)} != own URL {url}")

    for img in re.findall(r"<img\b[^>]*>", text):
        if not re.search(r'\balt=(?:"[^"]+"|[^\s>]+)', img):
            errors.append(f"{rel}: <img> without non-empty alt: {img[:80]}")
        if not re.search(r'\bwidth="?(\d+)', img) or not re.search(r'\bheight="?(\d+)', img):
            errors.append(f"{rel}: <img> without width/height: {img[:80]}")

    for block in re.findall(r'<script\s+type="?application/ld\+json"?>(.*?)</script>', text, re.S):
        try:
            json.loads(block)
            jsonld_pages.add(rel)
        except json.JSONDecodeError as e:
            errors.append(f"{rel}: JSON-LD does not parse: {e}")

    if not re.search(r"<h1[\s>]", text):
        errors.append(f"{rel}: no <h1> found")

for must in ("index.html",):
    if must not in jsonld_pages:
        errors.append(f"{must}: expected at least one JSON-LD block")
for rel in jsonld_pages:
    pass
post_pages = [f.relative_to(pub).as_posix() for f in html_files
              if re.match(r"posts/\d{4}/[^/]+/index\.html", f.relative_to(pub).as_posix())]
for rel in post_pages:
    if rel not in jsonld_pages:
        errors.append(f"{rel}: post page without JSON-LD")

# sitemap coverage
sitemap = pub / "sitemap.xml"
if not sitemap.exists():
    errors.append("sitemap.xml missing")
else:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = {el.text.strip() for el in ET.parse(sitemap).getroot().findall(".//sm:loc", ns)}
    for f in html_files:
        rel = f.relative_to(pub).as_posix()
        if rel == "404.html":
            continue
        u = url_for(f)
        if rel in REDIRECTS:
            if u in locs:
                errors.append(f"sitemap.xml lists redirect page {u}")
            continue
        if u not in locs:
            errors.append(f"sitemap.xml does not list {u}")

robots = pub / "robots.txt"
if not robots.exists():
    errors.append("robots.txt missing")
elif "Sitemap:" not in robots.read_text(encoding="utf-8"):
    errors.append("robots.txt does not reference the sitemap")

print(f"checked {len(html_files)} HTML pages, {len(descriptions)} descriptions, "
      f"{len(post_pages)} post pages, JSON-LD on {len(jsonld_pages)} pages")
for w in warnings:
    print("WARN:", w)
if errors:
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)
print("SEO CHECK: ALL PASS")
