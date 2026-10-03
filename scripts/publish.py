#!/usr/bin/env python3
"""Put a built site into a checkout of the gh-pages branch, as Documenter does.

    python3 scripts/publish.py <gh-pages dir> <site dir> <dest> [<dest> ...]
    python3 scripts/publish.py <gh-pages dir> --remove <dest> [<dest> ...]

The gh-pages branch holds one copy of the site per version, side by side:

    v0.10.0/  v0.11.0/  ...   one per release, kept
    stable/                   the newest release
    previews/PR<n>/           a pull request's site, while it is open
    versions.json             the versions, newest first, for the switcher in
                              each page's header (scripts/pages.py)
    index.html                a redirect to stable/

Each <dest> is replaced by the site whole; --remove deletes them. Either way
versions.json, index.html and .nojekyll are written again from what is there.
The workflows (.github/workflows/Documenter.yml, DocumenterPreview.yml) do the
git around it. Standard library only.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys

REDIRECT = """<!doctype html>
<meta charset="utf-8">
<title>tikz-tensors</title>
<meta http-equiv="refresh" content="0; url=stable/">
<link rel="canonical" href="stable/">
<a href="stable/">tikz-tensors documentation</a>
"""


def semver(name: str) -> tuple[int, ...]:
    return tuple(int(x) for x in name[1:].split("."))


def index(root: pathlib.Path) -> list[str]:
    """Rewrite versions.json, the redirect and .nojekyll; the versions, newest first."""
    released = sorted((p.name for p in root.iterdir()
                       if p.is_dir() and re.fullmatch(r"v\d+\.\d+\.\d+", p.name)),
                      key=semver, reverse=True)
    versions = (["stable"] if (root / "stable").is_dir() else []) + released
    (root / "versions.json").write_text(json.dumps(versions, indent=1) + "\n")
    (root / "index.html").write_text(REDIRECT)
    (root / ".nojekyll").write_text("")
    return versions


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        sys.exit(__doc__)
    root = pathlib.Path(argv[0])
    root.mkdir(parents=True, exist_ok=True)
    if argv[1] == "--remove":
        for dest in argv[2:]:
            target = root / dest
            if target.exists():
                shutil.rmtree(target)
                print(f"removed {dest}/")
    else:
        site = pathlib.Path(argv[1])
        if not (site / "index.html").is_file():
            sys.exit(f"{site}: not a built site (no index.html)")
        for dest in argv[2:]:
            if not re.fullmatch(r"(stable|v\d+\.\d+\.\d+|previews/PR\d+)", dest):
                sys.exit(f"{dest}: not a place a site goes (stable, v<x.y.z>, previews/PR<n>)")
            target = root / dest
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(site, target)
            print(f"published {dest}/")
    print("versions:", ", ".join(index(root)) or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
