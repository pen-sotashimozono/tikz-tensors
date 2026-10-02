#!/usr/bin/env python3
"""Every public style and command of the package is drawn by some test case.

    python3 tests/coverage.py

The names come from scripts/version.py's `api` (what the version check guards);
a name counts as used when a file under tests/cases/ or examples/ mentions it.
A key that takes a value counts when it is used with one, hence the `=`, and a
style named in a \\tnchain spec counts, hence the `/`.
Colours and theme tokens are left out: tests/cases/styles.tex shows them as
swatches, and theme.py --check keeps them in step with theme/tokens.toml.

The package's style names are shapes, so none shares a name with a colour and
the textual match is a proof for each of them. The notation's styles (fn,
canl, ...) live in examples/conventions/ and are not the package's to cover.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import version  # noqa: E402

text = "\n".join(p.read_text() for d in ("tests/cases", "examples")
                 for p in sorted((ROOT / d).glob("*.tex")))
missing = []
for name in sorted(version.api()):
    what, _, ident = name.partition(" ")
    ident = ident.strip("'")
    if what == "style":
        used = re.search(rf"[\[,\s{{=]{re.escape(ident)}\s*[\],=/]", text)
    elif what == "command":
        used = re.search(re.escape(ident) + r"(?![A-Za-z])", text)
    else:
        continue
    if not used:
        missing.append(name)
for name in missing:
    print(f"FAIL  coverage: {name} is used by no file in tests/cases/ or examples/")
if not missing:
    print("  ok  coverage: every style and command is drawn by a test case")

# docs/api.md is the interface: every public name is on it, and every name on
# it is public. A key is looked for in the section of the commands it belongs
# to (`key=`, or `key` for one that takes no value).
FAMILY = {"connect": [r"\tnconnect"], "open": [r"\tnopen", r"\tnopenswap"],
          "join": [r"\tnjoin"], "rel": [r"\tneq", r"\tnapprox"], "set": [r"\tnset"],
          "stack": [r"\tnstack"], "grid": [r"\tngrid"]}
doc = (ROOT / "docs/api.md").read_text()
sections = re.split(r"^### ", doc, flags=re.M)
undocumented = []
api = version.api()
for name in sorted(api):
    what, _, ident = name.partition(" ")
    ident = ident.strip("'")
    if what in ("colour", "token"):
        continue
    if what == "key":
        family, key = ident.split("/", 1)
        heads = FAMILY.get(family, [])
        found = any(re.search(rf"`{re.escape(key)}(=|`)", sec)
                    for sec in sections
                    if any(sec.startswith(f"`{h}") or f"`{h}[" in sec.split("\n")[0]
                           for h in heads))
    else:
        found = f"`{ident}" in doc
    if not found:
        undocumented.append(name)
documented = ({f"command {m}" for m in re.findall(r"`(\\tn[a-z]+)", doc)} |
              {f"style '{m}'" for m in re.findall(r"`(tn [a-z ]+?)`", doc)})
unknown = sorted(documented - api)
for name in undocumented:
    print(f"FAIL  api: {name} is public and not in docs/api.md")
for name in unknown:
    print(f"FAIL  api: docs/api.md names {name}, which the package does not define")
if not undocumented and not unknown:
    print("  ok  api: docs/api.md lists the public names, and only them")
sys.exit(1 if missing or undocumented or unknown else 0)
