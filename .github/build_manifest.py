#!/usr/bin/env python3
"""Walk the repo and write manifest.json, which index.html renders.

Run by .github/workflows/manifest.yml on every push, so adding a deck is
just: commit the file, push, done. Nothing here needs editing when new
material arrives — only if you want a new file type listed.
"""
import datetime
import re
import json
import os
import subprocess

SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__", "data"}  # "data" = raw files notebooks fetch, not course material
KINDS = {".html": "deck", ".ipynb": "notebook", ".pdf": "pdf"}
# HTML files named like "07 http_explorer.html" are interactive demos, not decks
DEMO_RE = re.compile(r"^\d\d ")

# Optional: nicer names for folders. Anything not listed falls back to the
# folder name with dashes/underscores turned into spaces and title-cased.
SECTION_TITLES = {
    ".": "Introduction",
    "intro": "Introduction · pandas",
    "data cleaning": "Data cleaning · regular expressions",
    "data-cleaning": "Data cleaning · regular expressions",
    "data collection": "Data collection · web scraping",
    "data-collection": "Data collection · web scraping",
}


def last_commit_date(path):
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", path],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip()
        return out[:10]
    except Exception:
        return ""


def main():
    items = []
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = sorted(
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
        )
        for name in sorted(filenames):
            ext = os.path.splitext(name)[1].lower()
            if ext not in KINDS or name == "index.html":
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), ".").replace(os.sep, "/")
            folder = os.path.dirname(rel) or "."
            items.append({
                "path": rel,
                "name": name,
                "folder": folder,
                "section": SECTION_TITLES.get(folder, folder.replace("-", " ").replace("_", " ").title()),
                "kind": "demo" if (ext == ".html" and DEMO_RE.match(name)) else KINDS[ext],
                "size": os.path.getsize(rel),
                "updated": last_commit_date(rel),
            })

    manifest = {
        "repo": os.environ.get("GITHUB_REPOSITORY", ""),
        "branch": os.environ.get("GITHUB_REF_NAME", ""),
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "items": items,
    }
    with open("manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"manifest.json: {len(items)} files")


if __name__ == "__main__":
    main()
