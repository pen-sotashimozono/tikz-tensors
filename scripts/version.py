#!/usr/bin/env python3
"""The package's version: read it, bump it, and check a change moved it right.

    python3 scripts/version.py [--ref v0.2.0]          # print the version (0.2.0)
    python3 scripts/version.py bump minor "Why."       # bump + CHANGELOG entry
    python3 scripts/version.py check --base origin/main
    python3 scripts/version.py notes v0.2.0            # that version's CHANGELOG body

The version lives in one place, the \\ProvidesPackage line of
tex/tikz-tensors.sty, which is also what a document sees in its log. Tags are
v<version>; CHANGELOG.md has one section per version, headed by its tag.

`check` compares the working tree with a base commit and enforces semantic
versioning on the package's public names -- TikZ styles, commands, colours and
theme tokens (see `api`) -- and on how the tests render:

    a public name removed            -> major   (minor before 1.0.0)
    a name added, or a reference
    image in tests/reference changed
    or removed (a new one is not)    -> minor
    anything else under tex/, theme/ -> patch
    nothing under tex/, theme/       -> the version must not move

The bump must be exactly one step, at least that large, and CHANGELOG.md must
open with a filled-in section for it. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
STY = "tex/tikz-tensors.sty"
CHANGELOG = "CHANGELOG.md"
PACKAGE = ("tex/", "theme/")
PROVIDES = re.compile(r"(\\ProvidesPackage\{tikz-tensors\}\[)(\d{4}/\d{2}/\d{2}) v(\d+\.\d+\.\d+)( [^\]]*\])")
LEVELS = ("patch", "minor", "major")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def read(path: str, ref: str | None = None) -> str | None:
    """A file from the working tree, or from a commit (None if absent there)."""
    if ref is None:
        p = ROOT / path
        return p.read_text() if p.exists() else None
    out = git("show", f"{ref}:{path}")
    return out.stdout if out.returncode == 0 else None


def files(ref: str | None, prefix: str) -> list[str]:
    if ref is None:
        return sorted(str(p.relative_to(ROOT)) for p in (ROOT / prefix).rglob("*") if p.is_file())
    out = git("ls-tree", "-r", "--name-only", ref, prefix)
    if out.returncode:
        sys.exit(f"git ls-tree {ref} failed: {out.stderr.strip()}")
    return out.stdout.split()


def version(ref: str | None = None) -> str:
    m = PROVIDES.search(read(STY, ref) or "")
    if not m:
        sys.exit(f"no \\ProvidesPackage{{tikz-tensors}}[YYYY/MM/DD vX.Y.Z ...] in {STY}"
                 + (f" at {ref}" if ref else ""))
    return m.group(3)


def parse(v: str) -> tuple[int, int, int]:
    major, minor, patch = (int(x) for x in v.split("."))
    return major, minor, patch


def step(v: str, level: str) -> str:
    major, minor, patch = parse(v)
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def level_of(old: str, new: str) -> str | None:
    """Which single step takes old to new, or None if it is not one step."""
    return next((level for level in LEVELS if step(old, level) == new), None)


def api(ref: str | None = None) -> set[str]:
    """The public names: what a document or a page can refer to."""
    names: set[str] = set()
    for path in files(ref, "tex/"):
        text = read(path, ref) or ""
        names |= {f"style '{n.strip()}'" for n in re.findall(r"([\w ]+?)/\.style", text)}
        names |= {f"command \\{n}" for n in re.findall(r"\\(?:new|provide)command\*?\{\\(\w+)\}", text)}
        names |= {f"colour {n}" for n in re.findall(r"\\definecolor\{(\w+)\}", text)}
    css = read("theme/theme.css", ref) or ""
    names |= {f"token --{n}" for n in re.findall(r"--([\w-]+):", css)}
    return names


def changed(base: str) -> dict[str, str]:
    """{path: A|M|D|...} between base and the working tree, untracked files as A."""
    diff = git("diff", "--name-status", "--no-renames", base, "--")
    if diff.returncode:
        sys.exit(f"git diff {base} failed: {diff.stderr.strip()}")
    status = {path: kind[0] for kind, path in
              (line.split("\t", 1) for line in diff.stdout.splitlines() if line)}
    for path in git("ls-files", "--others", "--exclude-standard").stdout.split():
        status[path] = "A"
    return status


def changelog_section(tag: str) -> str | None:
    text = read(CHANGELOG) or ""
    m = re.search(rf"^## {re.escape(tag)}(?![\w.])[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else None


def required(base: str, old: str) -> tuple[str | None, str]:
    """The smallest bump this change needs (None: none allowed), and why."""
    touched = changed(base)
    # The \ProvidesPackage line is the version itself, not a change to the package.
    if STY in touched and PROVIDES.sub("", read(STY, base) or "") == PROVIDES.sub("", read(STY) or ""):
        del touched[STY]
    package = sorted(f for f in touched if f.startswith(PACKAGE))
    refs = sorted(f for f, kind in touched.items()
                  if f.startswith("tests/reference/") and kind != "A")
    if not package and not refs:
        return None, "changes nothing under tex/ or theme/ and no reference image"
    removed = sorted(api(base) - api())
    if removed:
        return ("major" if parse(old)[0] >= 1 else "minor"), "removes " + ", ".join(removed)
    added = sorted(api() - api(base))
    if added:
        return "minor", "adds " + ", ".join(added)
    if refs:
        return "minor", "changes how " + ", ".join(refs) + " render"
    return "patch", "changes " + ", ".join(package)


def check(base: str) -> int:
    old, new = version(base), version()
    need, why = required(base, old)
    errors: list[str] = []
    if need is None:
        if new != old:
            errors.append(f"version moved {old} -> {new}, but this {why}. Put it back to {old}.")
        else:
            print(f"this {why}; version stays {old}. OK")
    else:
        got = level_of(old, new)
        if new == old:
            errors.append(f"this {why}, so the version must move by a {need} step at least "
                          f"(python3 scripts/version.py bump {need} \"Why.\"), but it is still {old}.")
        elif got is None:
            errors.append(f"version moved {old} -> {new}, which is not one step (patch "
                          f"{step(old, 'patch')}, minor {step(old, 'minor')}, major {step(old, 'major')}).")
        elif LEVELS.index(got) < LEVELS.index(need):
            errors.append(f"this {why}, which needs a {need} step ({step(old, need)}), "
                          f"but the version moved by a {got} step to {new}.")
        else:
            print(f"{old} -> {new}, a {got} step; this {why}. OK")
    if new != old:
        body = changelog_section(f"v{new}")
        first = re.search(r"^## (v\S+)", read(CHANGELOG) or "", re.M)
        if body is None:
            errors.append(f"{CHANGELOG} has no '## v{new}' section.")
        elif not body or "TODO" in body:
            errors.append(f"{CHANGELOG}: the v{new} section is empty or still says TODO.")
        elif first and first.group(1) != f"v{new}":
            errors.append(f"{CHANGELOG} must open with v{new}, not {first.group(1)}.")
    for e in errors:
        print(f"::error::{e}")
    return 1 if errors else 0


def bump(level: str, summary: str) -> int:
    path, log = ROOT / STY, ROOT / CHANGELOG
    old = version()
    new = step(old, level)
    today = datetime.date.today()
    path.write_text(PROVIDES.sub(
        lambda m: f"{m.group(1)}{today.strftime('%Y/%m/%d')} v{new}{m.group(4)}",
        path.read_text(), count=1))
    text = log.read_text() if log.exists() else "# Changelog\n\n"
    entry = f"## v{new} — {today.isoformat()}\n\n{summary.strip() or 'TODO'}\n\n"
    m = re.search(r"^## ", text, re.M)
    log.write_text(text[:m.start()] + entry + text[m.start():] if m
                   else text.rstrip("\n") + "\n\n" + entry)
    print(f"{old} -> {new}: {STY}, {CHANGELOG}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command")
    b = sub.add_parser("bump", help="move the version one step and open its CHANGELOG entry")
    b.add_argument("level", choices=LEVELS)
    b.add_argument("summary", nargs="?", default="")
    c = sub.add_parser("check", help="the version moved exactly as the change requires")
    c.add_argument("--base", required=True, help="commit to compare against (origin/main)")
    n = sub.add_parser("notes", help="print one version's CHANGELOG section")
    n.add_argument("tag")
    parser.add_argument("--ref", help="print the version at this commit or tag instead")
    args = parser.parse_args()
    if args.command == "bump":
        return bump(args.level, args.summary)
    if args.command == "check":
        return check(args.base)
    if args.command == "notes":
        body = changelog_section(args.tag)
        if body is None:
            sys.exit(f"{CHANGELOG} has no '## {args.tag}' section")
        print(body)
        return 0
    print(version(args.ref))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
