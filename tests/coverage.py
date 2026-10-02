#!/usr/bin/env python3
"""Every public style and command of the package is drawn by some test case.

    python3 tests/coverage.py

The names come from scripts/version.py's `api` (what the version check guards);
a name counts as used when a file under tests/cases/ or examples/ mentions it.
The two `tn swap <kind>` styles are drawn by \\tnswap[<kind>] (cont by default).
A key that takes a value counts when it is used with one, hence the `=`, and a
style named in a \\tnchain spec counts, hence the `/`.
Colours and theme tokens are left out: tests/cases/styles.tex shows them as
swatches, and theme.py --check keeps them in step with theme/tokens.toml.

The match is textual, which has one consequence worth knowing: where a style
and a colour share a name (coef, centre, mpo, gate), the colour's swatch
satisfies the style. `gate' is like that -- it is applied by \\tngate and is
genuinely drawn, but what the check finds is the name in the swatch list. For
those four the check prompts rather than proves.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import version  # noqa: E402

text = "\n".join(p.read_text() for d in ("tests/cases", "examples")
                 for p in sorted((ROOT / d).glob("*.tex")))
kinds = set(re.findall(r"\\tnswap\[(\w+)\]", text))
if re.search(r"\\tnswap\s*\{", text):
    kinds.add("cont")
missing = []
for name in sorted(version.api()):
    what, _, ident = name.partition(" ")
    ident = ident.strip("'")
    if what == "style":
        used = (ident.split()[-1] in kinds) if ident.startswith("tn swap ") \
            else re.search(rf"[\[,\s]{re.escape(ident)}\s*[\],=/]", text)
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
sys.exit(1 if missing else 0)
