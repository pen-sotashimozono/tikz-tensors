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
# ?sanitize=true makes raw.githubusercontent.com serve an SVG as an image, so
# GitHub shows it inline instead of as text.
RAW = "https://raw.githubusercontent.com/{repo}/{sha}/tests/reference/{name}.svg?sanitize=true"


def changed(base: str) -> list[str]:
    """Page stems whose source or picture differs from base, in a stable order."""
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", f"{base}...HEAD", "--", *WATCHED],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    stems = {pathlib.PurePath(p).stem for p in out.split() if p.endswith((".tex", ".svg"))}
    return sorted(s for s in stems if (ROOT / f"tests/reference/{s}.svg").is_file())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True)
    ap.add_argument("--sha", required=True)
    ap.add_argument("--repo", required=True)
    a = ap.parse_args()

    pages = changed(a.base)
    print("### Figure preview\n")
    if not pages:
        print("No page is drawn differently from the base.")
        return 0
    for name in pages:
        src = next((f"{d}/{name}.tex" for d in ("examples", "tests/cases")
                    if (ROOT / d / f"{name}.tex").is_file()), None)
        url = RAW.format(repo=a.repo, sha=a.sha, name=name)
        print(f"**{name}**" + (f" — `{src}`" if src else "") + "\n")
        print(f"![{name}]({url})\n")
        # The link in full, under the picture: a reader who cannot see the
        # image -- or wants the file itself -- should not have to go hunting
        # for a run summary or an artifact.
        print(f"{url}\n")
    print("*(updates on each push to this PR)*")
    return 0


if __name__ == "__main__":
    sys.exit(main())
