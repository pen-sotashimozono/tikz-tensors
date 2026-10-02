#!/usr/bin/env python3
"""Compare rendered pages with the committed reference pictures.

    python3 tests/compare.py <rendered dir> [--update]

Every <name>.svg in the rendered directory (pdftocairo -svg output) is compared
with tests/reference/<name>.svg as a drawing, not as text and not as pixels:

- a page is the set of things it draws: every <path> outside <defs>, with its
  paint (fill, stroke, width), and every glyph placed by <use>, taken by the
  shape of the glyph it points at rather than by its id, which pdftocairo
  numbers in the order it meets them;
- two of them are the same thing when everything but their numbers agrees and
  every number is within EPSILON (in pt): a path that moved a hair is the same
  path, one that moved a leg's width is not;
- a page passes when its size agrees within EPSILON and at most TOLERANCE of
  the things on either side have no partner on the other.

So a moved leg, a changed colour, a lost label or a new tensor fails, and the
order of the file, the numbering of glyphs and the last digits of a number do
not. Vector pictures also make the references small, readable in a diff, and
shown as they are by GitHub (README, the PR preview).

For a page that fails, <name>-diff.txt beside it lists what is only in the
reference and only in the render. --update copies the rendered pages over the
references. Writes a Markdown table to $GITHUB_STEP_SUMMARY when set. Standard
library only.
"""
from __future__ import annotations

import collections
import os
import pathlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET

REFERENCE = pathlib.Path(__file__).resolve().parent / "reference"
EPSILON = 0.25        # pt
TOLERANCE = 0.01      # fraction of the things drawn
SVG = "{http://www.w3.org/2000/svg}"
XLINK = "{http://www.w3.org/1999/xlink}href"
NUMBER = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?")
PAINT = ("fill", "fill-rule", "fill-opacity", "stroke", "stroke-width",
         "stroke-opacity", "stroke-dasharray", "stroke-linecap", "stroke-linejoin")


def split(text: str) -> tuple[str, tuple[float, ...]]:
    """A string as its skeleton (numbers replaced by #) and its numbers."""
    return NUMBER.sub("#", text), tuple(float(x) for x in NUMBER.findall(text))


def colour(value: str) -> str:
    """rgb(19.999695%, ...) to whole percent, so that a colour is one string."""
    return NUMBER.sub(lambda m: str(round(float(m.group()))), value)


def drawing(path: pathlib.Path) -> tuple[tuple[float, float], dict]:
    """(width, height) and {skeleton: [numbers, ...]} of everything drawn."""
    root = ET.parse(path).getroot()
    size = (float(NUMBER.search(root.get("width", "0")).group()),
            float(NUMBER.search(root.get("height", "0")).group()))
    glyphs = {}
    for g in root.iter(f"{SVG}g"):
        if g.get("id", "").startswith("glyph"):
            shape = " ".join(p.get("d", "") for p in g.iter(f"{SVG}path"))
            glyphs[g.get("id")] = NUMBER.sub(lambda m: f"{float(m.group()):.2f}", shape)
    things = collections.defaultdict(list)

    def walk(node, inherited):
        if node.tag == f"{SVG}defs":
            return
        paint = dict(inherited)
        for k in PAINT:
            if node.get(k) is not None:
                paint[k] = colour(node.get(k)) if "fill" in k or "stroke" == k else node.get(k)
        style = ";".join(f"{k}={paint[k]}" for k in sorted(paint))
        if node.tag == f"{SVG}path":
            skel, nums = split((node.get("transform") or "") + "|" + node.get("d", ""))
            things[f"path {style} {skel}"].append(nums)
        elif node.tag == f"{SVG}use":
            ref = (node.get(XLINK) or "").lstrip("#")
            things[f"glyph {style} {glyphs.get(ref, ref)}"].append(
                (float(node.get("x", 0)), float(node.get("y", 0))))
        for child in node:
            walk(child, paint)

    walk(root, {})
    return size, things


def unmatched(ref: dict, new: dict) -> tuple[list[str], list[str], int]:
    """What only the reference has, what only the render has, and the total."""
    only_ref, only_new, total = [], [], 0
    for key in sorted(set(ref) | set(new)):
        a, b = list(ref.get(key, [])), list(new.get(key, []))
        total += max(len(a), len(b))
        left = []
        for nums in a:
            for i, other in enumerate(b):
                if len(other) == len(nums) and all(
                        abs(x - y) <= EPSILON for x, y in zip(nums, other)):
                    del b[i]
                    break
            else:
                left.append(nums)
        short = key if len(key) < 100 else key[:97] + "..."
        only_ref += [f"{short} {n[:6]}" for n in left]
        only_new += [f"{short} {n[:6]}" for n in b]
    return only_ref, only_new, total


def compare(rendered: pathlib.Path) -> tuple[str, str]:
    name = rendered.stem
    ref = REFERENCE / f"{name}.svg"
    if not ref.is_file():
        return "new", "no reference picture; run tests/run.sh --update and commit it"
    (rw, rh), r = drawing(ref)
    (nw, nh), n = drawing(rendered)
    if abs(rw - nw) > EPSILON or abs(rh - nh) > EPSILON:
        return "FAIL", f"size {nw:.1f}x{nh:.1f}pt, reference {rw:.1f}x{rh:.1f}pt"
    only_ref, only_new, total = unmatched(r, n)
    bad = len(only_ref) + len(only_new)
    share = bad / max(total, 1)
    if share > TOLERANCE:
        diff = rendered.with_name(f"{name}-diff.txt")
        diff.write_text("only in the reference:\n" + "\n".join(only_ref) +
                        "\n\nonly in the render:\n" + "\n".join(only_new) + "\n")
        # The first few, in the log itself, so a failure on a runner can be read
        # without fetching the artifact.
        sample = ([f"      - {t}" for t in only_ref[:4]] +
                  [f"      + {t}" for t in only_new[:4]])
        return "FAIL", (f"{bad} of {total} drawn things differ ({share:.1%}, limit "
                        f"{TOLERANCE:.0%}); see {diff.name}\n" + "\n".join(sample))
    return "ok", f"{bad} of {total} drawn things differ"


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rendered = pathlib.Path(sys.argv[1])
    update = "--update" in sys.argv[2:]
    pages = sorted(p for p in rendered.glob("*.svg"))
    if update:
        REFERENCE.mkdir(exist_ok=True)
        for p in pages:
            shutil.copy(p, REFERENCE / p.name)
        print(f"updated {len(pages)} reference pictures in tests/reference/")
        return 0
    fail, rows = 0, []
    for p in pages:
        status, detail = compare(p)
        print(f"{status:>4}  {p.stem}: {detail}")
        rows.append((p.stem, status, detail))
        fail |= status != "ok"
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write("| page | result | detail |\n|---|---|---|\n")
            for row in rows:
                f.write("| " + " | ".join(row) + " |\n")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
