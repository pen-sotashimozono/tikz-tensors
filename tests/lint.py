#!/usr/bin/env python3
"""The figure rules: an example states topology and roles, the package does the rest.

    python3 tests/lint.py               # every example under examples/
    python3 tests/lint.py FILE ...      # just these

docs/roadmap.md says why. Two people who draw the same algorithm should write
the same file, and what makes Go code converge is a tool, not a style guide;
this is that tool for the figures. A finding is a place where a second author
-- or a second LLM run -- would choose differently, and the fix for one is a
command or a token in tex/, never a number in the figure.

What is checked, on the file with its comments and its math removed:

  frame     the file is the one frame and nothing else: the fixed preamble
            (the package, then the notation the figure is drawn in --
            examples/conventions/notation.tex), one tikzpicture with no
            options, and the end
  length    no length and no decimal: every distance is the package's
  coord     no literal coordinate (x,y): a tensor sits on a slot, not a point
  key       no key that sets what a role decides or moves a thing by hand
            (fill=, draw=, minimum width=, xshift=, anchor=, ...)
  command   no raw TikZ or TeX: \\node, \\draw, \\path, scope, \\tikzset,
            \\newcommand, \\def, \\pgfmath... -- a pattern a figure needs is a
            command in tex/; and not the package's own escape hatches,
            \\tnbond (a path written out) and \\tnset (the tokens, which are a
            notation's to change)

  repeat    a run of like entries in a \\tnlayer is written once, <n>*<entry>,
            and the whole run in one: 3*canl/$A$, never canl/$A$, canl/$A$,
            canl/$A$ or 2*canl/$A$, canl/$A$ -- so a layer has one spelling

Rules 5 and 6 of the roadmap (fixed names, one order of statements) are not
checked yet: they are about commands that do not exist yet, and are added here
with them.

The examples written before the rules are listed in tests/lint-legacy.txt and
are exempt. The list may only shrink: a listed file that passes is an error
too, so the line goes in the same change that makes the file pass.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEGACY = ROOT / "tests" / "lint-legacy.txt"

# Not figures, so not under the rules at all.
EXEMPT = {
    "00-palette.tex": "a swatch sheet of the theme, not a diagram",
}

HEAD = [r"\documentclass[border=4pt]{standalone}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{tikz-tensors}",
        r"\input{notation}",
        r"\begin{document}",
        r"\begin{tikzpicture}"]
TAIL = [r"\end{tikzpicture}",
        r"\end{document}"]

UNIT = r"(?:mm|cm|pt|bp|em|ex|in|sp|pc)"
RULES = [
    ("length", re.compile(rf"\d*\.?\d+\s*{UNIT}\b|\d*\.\d+")),
    ("coord", re.compile(r"\(\s*[-+]?\s*[\d.]+\s*,\s*[-+]?\s*[\d.]+\s*\)")),
    ("key", re.compile(
        r"\b(?:fill|draw|color|text|shape|minimum (?:width|height|size)"
        r"|inner sep|outer sep|xshift|yshift|shift|x|y|scale|rotate|anchor"
        r"|line width)\s*=")),
    ("command", re.compile(
        r"\\(?:node|draw|path|fill|filldraw|coordinate|clip|matrix"
        r"|tikzset|newcommand|renewcommand|def|let|edef|gdef|tnbond|tnset"
        r"|pgf[a-z]*)(?![A-Za-z@])"
        r"|\\(?:begin|end)\{(?:scope|pgfonlayer)\}")),
]


def strip_comment(line):
    """The line without its comment: a % not escaped by a backslash."""
    return re.split(r"(?<!\\)%", line, maxsplit=1)[0].rstrip()


def strip_math(line):
    """Math is a label's text, never layout, so it is not checked."""
    return re.sub(r"(?<!\\)\$[^$]*(?<!\\)\$", "$$", line)


def lint(path):
    """Every finding in one file, as (line number, rule, text)."""
    lines = [(n, strip_comment(raw))
             for n, raw in enumerate(path.read_text().splitlines(), 1)]
    lines = [(n, s) for n, s in lines if s.strip()]
    found = []

    # The frame: the fixed preamble up to a bare \begin{tikzpicture}, and the
    # fixed end after the last \end{tikzpicture}. Anything else outside the
    # picture is a finding of its own, on its own line.
    texts = [s.strip() for _, s in lines]
    opens = [i for i, t in enumerate(texts) if t.startswith(r"\begin{tikzpicture}")]
    closes = [i for i, t in enumerate(texts) if t == TAIL[0]]
    if not opens or not closes:
        return [(lines[0][0] if lines else 1, "frame", "no tikzpicture")]
    first, last = opens[0], closes[-1]
    if texts[first] != HEAD[-1]:
        found.append((lines[first][0], "frame",
                      "the picture takes no options: " + texts[first]))
    pre = texts[:first]
    for i, t in enumerate(pre):
        if t not in HEAD[:-1]:
            found.append((lines[i][0], "frame", "outside the picture: " + t))
    if [t for t in pre if t in HEAD[:-1]] != HEAD[:-1]:
        found.append((lines[0][0], "frame", "the preamble is not the standard one"))
    if texts[last:] != TAIL:
        found.append((lines[last][0], "frame",
                      "does not end with \\end{tikzpicture} \\end{document}"))
    body = lines[first + 1:last]
    for n, s in body:
        if s.strip() in HEAD + TAIL:
            found.append((n, "frame", f"one picture per file: {s.strip()}"))
    # what sits outside the picture is checked as well
    body = [(n, s) for n, s in lines[:first] if s.strip() not in HEAD] + body

    for n, s in body:
        text = strip_math(s)
        for rule, pattern in RULES:
            for m in pattern.finditer(text):
                found.append((n, rule, m.group(0).strip()))
    found += repeats(body)
    found.sort(key=lambda f: f[0])
    return found


def groups(text, start, count):
    """The next <count> brace groups of text from <start>, and where they end."""
    out, i = [], start
    for _ in range(count):
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] != "{":
            return None, i
        depth, j = 0, i
        while j < len(text):
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            if depth == 0:
                break
            j += 1
        out.append(text[i + 1:j])
        i = j + 1
    return out, i


def entries(text):
    """A \\tnlayer list split at its top-level commas, each as (count, entry)."""
    parts, depth, cur = [], 0, ""
    for c in text:
        depth += {"{": 1, "}": -1}.get(c, 0)
        if c == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    parts.append(cur)
    out = []
    for p in (" ".join(p.split()) for p in parts):
        m = re.match(r"(\d+)\s*\*\s*(.*)", p)
        out.append((int(m.group(1)), m.group(2), True) if m else (1, p, False))
    return out


def repeats(body):
    """Runs of like entries in a \\tnlayer not written as one <n>*<entry>."""
    found = []
    text = "\n".join(s for _, s in body)
    starts = [n for n, s in body for _ in [0] for _ in s + "\n"]
    for m in re.finditer(r"\\tnlayer(?![A-Za-z@])", text):
        args, _ = groups(text, m.end(), 3)
        if args is None:
            continue
        n = starts[m.start()]
        layer = entries(args[2])
        for (k, e, star), (_, f, _) in zip(layer, layer[1:] + [(0, None, False)]):
            if e == f:
                found.append((n, "repeat", f"{e}, {f} -- one run, written <n>*{e}"))
        for k, e, star in layer:
            if star and k < 2:
                found.append((n, "repeat", f"{k}*{e} -- a run is two or more"))
    return found


def figures():
    return sorted(p for p in (ROOT / "examples").glob("*.tex")
                  if p.name not in EXEMPT)


def legacy():
    if not LEGACY.exists():
        return set()
    return {line.split("#")[0].strip() for line in LEGACY.read_text().splitlines()
            if line.split("#")[0].strip()}


def main(argv):
    paths = [pathlib.Path(a).resolve() for a in argv] or figures()
    exempt = legacy()
    fail = False
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        found = lint(path)
        if rel in exempt:
            if not found:
                print(f"FAIL  {rel}: passes the rules; take it off "
                      f"{LEGACY.relative_to(ROOT)}")
                fail = True
            continue
        for n, rule, text in found:
            print(f"{rel}:{n}: {rule}: {text}")
        if found:
            fail = True
    stale = exempt - {p.relative_to(ROOT).as_posix() for p in figures()}
    if not argv and stale:
        for rel in sorted(stale):
            print(f"FAIL  {LEGACY.relative_to(ROOT)}: {rel} is not an example")
        fail = True
    if not fail:
        held = sum(p.relative_to(ROOT).as_posix() in exempt for p in paths)
        print(f"  ok  lint: {len(paths) - held} figure(s) follow the rules, "
              f"{held} legacy")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
