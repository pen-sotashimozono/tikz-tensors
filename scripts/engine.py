#!/usr/bin/env python3
"""Fetch the TeX that runs in a browser, for the documentation site's live pages.

    python3 scripts/engine.py [DIR]      # into DIR (default .engine/)

TikZJax is TeX compiled to WebAssembly, with LaTeX and TikZ in its memory
image, that turns a tikzpicture on a web page into SVG in the reader's
browser; it fetches each file TeX opens from tex_files/<name>.gz beside it.
scripts/pages.py copies it to the site's live/ with the package's own files
gzipped into that directory, so a figure can be edited and drawn again on the
page with nothing installed (live.html, and `Edit live' on every example).

It is the build of drgrice1/tikzjax on npm, pinned here by version and by the
registry's SHA-512, and served unmodified; it is GPL-3.0-or-later, and the
page that loads it says so and links its source. Standard library only.
"""
from __future__ import annotations

import base64
import hashlib
import io
import pathlib
import shutil
import sys
import tarfile
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSION = "1.0.0-beta24"
URL = f"https://registry.npmjs.org/@drgrice1/tikzjax/-/tikzjax-{VERSION}.tgz"
SHA512 = "QUrbP01XfNWSfN/V0wR+Lh1f3VWyo1wN2FwHxx7jfgPN47xtwnNi5vfRHapB8KUZCjclrw0TvI7Fnh9dFFzdyA=="
SOURCE = "https://github.com/drgrice1/tikzjax"


def fetch(out: pathlib.Path) -> pathlib.Path:
    """The engine in <out>, fetched unless it is there at this version already."""
    stamp = out / "VERSION"
    if stamp.is_file() and stamp.read_text().strip() == VERSION:
        return out
    with urllib.request.urlopen(URL, timeout=120) as r:
        data = r.read()
    got = base64.b64encode(hashlib.sha512(data).digest()).decode()
    if got != SHA512:
        sys.exit(f"{URL}: SHA-512 {got}, expected {SHA512}")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for m in tar.getmembers():
            if not m.isfile() or not m.name.startswith("package/dist/") or m.name.endswith(".map"):
                continue
            dest = out / m.name[len("package/dist/"):]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(tar.extractfile(m).read())
    stamp.write_text(VERSION + "\n")
    return out


if __name__ == "__main__":
    where = fetch(pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".engine")
    print(f"TikZJax {VERSION} in {where}")
