#!/usr/bin/env python3
"""Compare rendered pages with the committed reference images.

    python3 tests/compare.py <rendered dir> [--update]

Every <name>.png in the rendered directory (pdftocairo -png output) is compared
with tests/reference/<name>.png. A page passes when it has the same size and
at most TOLERANCE of its drawn pixels (not white in either image) differ by
more than THRESHOLD levels in some colour channel, so a blue that turns grey
counts, not only a moved line. Measuring against what is drawn, not the whole
page, keeps a small diagram on a large page as sensitive as a cropped one.
The limits absorb anti-aliasing between poppler and TeX Live versions, not a
moved leg, a changed colour or a lost label. For a page that
fails, <name>-diff.png beside it shows the reference faintly, with differing
pixels in red. --update copies the rendered pages over the references.

Writes a Markdown table to $GITHUB_STEP_SUMMARY when set. Standard library
only: a decoder for the 8-bit RGB / greyscale PNGs pdftocairo writes, and an
encoder.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import struct
import sys
import zlib

REFERENCE = pathlib.Path(__file__).resolve().parent / "reference"
THRESHOLD = 64        # levels (of 255) in any channel
TOLERANCE = 0.01      # fraction of the drawn pixels
WHITE = 250           # a pixel with every channel above this is paper


def read_png(path: pathlib.Path) -> tuple[int, int, bytearray]:
    """(width, height, RGB bytes) of an 8-bit RGB or greyscale, non-interlaced PNG."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos, idat, width, height, n = 8, bytearray(), 0, 0, 3
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or colour not in (0, 2) or interlace:
                raise ValueError(f"{path}: expected 8-bit RGB or greyscale, non-interlaced "
                                 f"(as pdftocairo -png writes)")
            n = 3 if colour == 2 else 1
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    raw = zlib.decompress(bytes(idat))
    stride = width * n
    out = bytearray(stride * height)
    prev = bytearray(stride)
    for y in range(height):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = line[x - n] if x >= n else 0
            b = prev[x]
            c = prev[x - n] if x >= n else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        out[y * stride:(y + 1) * stride] = line
        prev = line
    if n == 1:
        out = bytearray(v for v in out for _ in range(3))
    return width, height, out


def write_png(path: pathlib.Path, width: int, height: int, pixels: bytes) -> None:
    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    stride = width * 3
    raw = b"".join(b"\0" + bytes(pixels[y * stride:(y + 1) * stride]) for y in range(height))
    path.write_bytes(b"\x89PNG\r\n\x1a\n"
                     + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def compare(rendered: pathlib.Path) -> tuple[str, str]:
    """(status, detail) for one rendered page against its reference."""
    ref = REFERENCE / rendered.name
    if not ref.exists():
        return "new", "no reference image; run tests/run.sh --update and commit it"
    w1, h1, a = read_png(ref)
    w2, h2, b = read_png(rendered)
    if (w1, h1) != (w2, h2):
        return "FAIL", f"size {w2}x{h2}, reference {w1}x{h1}"
    bad, drawn = [], 0
    for i in range(0, len(a), 3):
        if min(a[i:i + 3]) <= WHITE or min(b[i:i + 3]) <= WHITE:
            drawn += 1
            if max(abs(a[i + k] - b[i + k]) for k in range(3)) > THRESHOLD:
                bad.append(i)
    share = len(bad) / max(drawn, 1)
    if share <= TOLERANCE:
        return "ok", f"{share:.3%} of drawn pixels differ"
    diff = bytearray(200 + p * 55 // 255 for p in a)
    for i in bad:
        diff[i:i + 3] = b"\xd0\x00\x00"
    write_png(rendered.with_name(rendered.stem + "-diff.png"), w1, h1, diff)
    return "FAIL", (f"{share:.3%} of drawn pixels differ (limit {TOLERANCE:.0%}); "
                    f"see {rendered.stem}-diff.png")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--update"]
    if len(args) != 1:
        sys.exit(__doc__)
    rendered = sorted(p for p in pathlib.Path(args[0]).glob("*.png") if not p.stem.endswith("-diff"))
    if not rendered:
        sys.exit(f"no rendered pages in {args[0]}")
    if "--update" in sys.argv:
        REFERENCE.mkdir(exist_ok=True)
        for p in rendered:
            shutil.copy(p, REFERENCE / p.name)
        names = {p.name for p in rendered}
        for old in REFERENCE.glob("*.png"):
            if old.name not in names:
                old.unlink()
        print(f"updated {len(rendered)} reference images in tests/reference/")
        return 0
    rows, failed = [], 0
    for p in rendered:
        status, detail = compare(p)
        failed += status != "ok"
        rows.append(f"| `{p.stem}` | {status} | {detail} |")
        print(f"{status:>4}  {p.stem}: {detail}")
    for name in sorted({r.name for r in REFERENCE.glob("*.png")} - {p.name for p in rendered}):
        failed += 1
        rows.append(f"| `{name[:-4]}` | FAIL | reference with no page; remove it (--update) |")
        print(f"FAIL  {name}: reference with no page")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write("### Appearance against tests/reference\n\n| page | | |\n|---|---|---|\n"
                    + "\n".join(rows) + "\n\nThe rendered pages and any diffs are in the "
                    "`rendered` artifact.\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
