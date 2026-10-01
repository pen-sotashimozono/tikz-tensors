#!/usr/bin/env python3
"""Markdown showing every page this branch draws differently from its base.

    python3 scripts/preview.py --base <ref> --sha <sha> --repo <owner/name>

A reference image is committed for every page, and tests/run.sh passes only when
the page renders to it exactly, so on a green run the committed image is what CI
drew. That lets a preview be links to this branch's own files -- no hosting, no
artifact to download -- which is why this prints markdown rather than copying
pictures anywhere.

A page is shown when its source changed (examples/, tests/cases/) or when its
picture changed (tests/reference/), the second catching a style edit that moves
a page nobody touched. Standard library only.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WATCHED = ("examples", "tests/cases", "tests/reference")
RAW = "https://raw.githubusercontent.com/{repo}/{sha}/tests/reference/{name}.png"


def changed(base: str) -> list[str]:
    """Page stems whose source or picture differs from base, in a stable order."""
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", f"{base}...HEAD", "--", *WATCHED],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    stems = {pathlib.PurePath(p).stem for p in out.split() if p.endswith((".tex", ".png"))}
    return sorted(s for s in stems if (ROOT / f"tests/reference/{s}.png").is_file())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True)
    ap.add_argument("--sha", required=True)
    ap.add_argument("--repo", required=True)
    a = ap.parse_args()

    pages = changed(a.base)
    if not pages:
        print("No page is drawn differently from the base.")
        return 0
    print(f"### Pages this branch draws differently\n")
    for name in pages:
        src = next((f"{d}/{name}.tex" for d in ("examples", "tests/cases")
                    if (ROOT / d / f"{name}.tex").is_file()), None)
        print(f"**{name}**" + (f" — `{src}`" if src else "") + "\n")
        print(f"![{name}]({RAW.format(repo=a.repo, sha=a.sha, name=name)})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
