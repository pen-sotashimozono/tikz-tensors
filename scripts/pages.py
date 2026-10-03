#!/usr/bin/env python3
"""Build the documentation site: the interface, and every example with its code.

    python3 scripts/pages.py [OUT]        # writes the site to OUT (default _site/)

Everything on it is read from the repository, so it cannot drift from it:

- the reference is docs/reference/, the pages tests/coverage.py holds to the
  code: index.md (`api.html`), commands.md and styles.md, whose pictures are
  docs/reference/styles/ and drawn by CI as the examples are;
- each example page shows the file in examples/ and the picture in
  tests/reference/ that CI checks that file draws -- the code beside the
  picture is the code that drew it;
- the notation page is examples/conventions/notation.tex;
- the colours are theme/theme.css, the theme the diagrams are drawn in, light
  and dark.

No TeX is needed: the pictures are the committed references. Standard library
only. The Documenter workflows publish it to gh-pages (scripts/publish.py):
each release, and a preview of each pull request; tests/test_pages.py builds
it and checks every link.
"""
from __future__ import annotations

import difflib
import gzip
import html
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = "https://github.com/pen-sotashimozono/tikz-tensors"
sys.path.insert(0, str(ROOT / "scripts"))
import version  # noqa: E402

NAV = [("index.html", "Overview"), ("examples.html", "Examples"), ("live.html", "Playground"),
       ("api.html", "Reference"), ("notation.html", "Notation")]


# ---- LaTeX, coloured -----------------------------------------------------------
TOKEN = re.compile(r"(?P<comment>(?<!\\)%.*)|(?P<math>(?<!\\)\$[^$\n]*\$)"
                   r"|(?P<cmd>\\(?:[A-Za-z@]+|.))|(?P<brace>[{}\[\]])")


REFERENCE = ROOT / "docs" / "reference"
# the reference's pages: its Markdown, the page it becomes, and its tab
REF_PAGES = [("index.md", "api.html", "Overview"), ("commands.md", "commands.html", "Commands"),
             ("styles.md", "styles.html", "Styles")]


REF_HTML = {h for _, h, _ in REF_PAGES}


def api_anchors() -> dict[str, str]:
    """Each public command and style to its place in the reference: the page
    and the id of the heading that names it (commands.html#tnopen)."""
    anchors = {}
    for md, html_name, _ in REF_PAGES[1:]:
        _, toc = markdown((REFERENCE / md).read_text(), code=False)
        for level, ident, text in toc:
            if level != 3:
                continue
            plain = html.unescape(re.sub(r"<[^>]+>", "", text))
            for name in re.findall(r"\\tn[a-z]+|\btn [a-z ]+?(?=,|$)", plain):
                anchors.setdefault(name, f"{html_name}#{ident}")
    return anchors


STYLE = re.compile(r"\btn (?:[a-z]+ )*?[a-z]+(?= *[,\]}=/])")


def latex(code: str, up: str | None = None) -> str:
    """LaTeX source as HTML, with comments, math, commands and braces marked.
    With <up> (the way to the site's root), a command of the package links to
    its entry in the reference, and a style of it (tn ...) to the styles."""
    links = ANCHORS if up is not None else {}
    styles = {n for n in links if n.startswith("tn ")}

    def text(t: str) -> str:
        if not styles:
            return html.escape(t)
        out, pos = [], 0
        for m in re.finditer("|".join(re.escape(n) for n in
                                      sorted(styles, key=len, reverse=True)), t):
            out.append(html.escape(t[pos:m.start()]))
            out.append(f'<a class="ref" href="{up}{links[m.group()]}">'
                       f'{html.escape(m.group())}</a>')
            pos = m.end()
        out.append(html.escape(t[pos:]))
        return "".join(out)

    out, pos = [], 0
    for m in TOKEN.finditer(code):
        out.append(text(code[pos:m.start()]))
        kind, word = m.lastgroup, m.group()
        span = f'<span class="tx-{kind}">{html.escape(word)}</span>'
        if kind == "cmd" and word in links:
            span = f'<a class="ref" href="{up}{links[word]}">{span}</a>'
        out.append(span)
        pos = m.end()
    out.append(text(code[pos:]))
    return "".join(out)


# ---- Markdown, the subset docs/reference/ uses ---------------------------------------
def inline(text: str) -> str:
    """Code spans, bold and links; the code spans are set aside first, so that
    bold may hold one and nothing inside one is read as Markdown."""
    codes: list[str] = []

    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\0{len(codes) - 1}\0"
    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{link(m.group(2))}">{m.group(1)}</a>', text)
    return re.sub(r"\0(\d+)\0", lambda m: codes[int(m.group(1))], text)


def prose(text: str) -> str:
    """A comment of a TeX file as text: its dashes and quotes, typeset."""
    text = text.replace("---", "\u2014").replace(" -- ", " \u2013 ")
    text = re.sub(r"`([^`']*)'", "\u2018\\1\u2019", text)
    return text


def autolink(text: str) -> str:
    """Escaped text with every web address in it a link -- a full one, or a
    site named by its domain alone (tensornetwork.org), which is linked as
    written. A full stop, comma or bracket after one is not part of it."""
    def a(m):
        url = m.group(1) or f"https://{m.group(2)}/"
        return f'<a href="{url}">{m.group()}</a>'
    return re.sub(r"(https?://[^\s<>()]*[^\s<>().,;:])"
                  r"|(?<![\w/.@-])((?:[a-z0-9-]+\.)+(?:org|com|net|io|dev))(?![\w/-])",
                  a, text)


def link(target: str) -> str:
    """A link in the repository's own Markdown, as one that works on the site."""
    if re.match(r"[a-z]+:", target) or target.startswith("#"):
        return target
    for md, html_name, _ in REF_PAGES:
        if target == md:
            return html_name
    return f"{REPO}/blob/main/{target.lstrip('./')}"


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>|\\", "", text.lower())).strip("-")


def markdown(text: str, code: bool = True) -> tuple[str, list[tuple[int, str, str]]]:
    """HTML for the Markdown, and its headings (level, id, text) for a contents list."""
    lines, out, toc = text.splitlines(), [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            body = chr(10).join(lines[i + 1:j])
            out.append(f'<pre class="code">{latex(body, "") if code else html.escape(body)}</pre>')
            i = j + 1
        elif m := re.match(r"(#{1,4}) (.*)", line):
            level, body = len(m.group(1)), inline(m.group(2))
            # a command's entry is anchored at its name: commands.html#tnopen
            name = re.match(r"`\\(tn[a-z]+)|`(tn [a-z ]+)`", m.group(2))
            ident = (name.group(1) or slug(name.group(2))) if name else slug(body)
            toc.append((level, ident, body))
            out.append(f'<h{level} id="{ident}">{body}</h{level}>')
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"\|[-| :]+\|$", lines[i]):
                    rows.append([c.strip() for c in
                                 re.split(r"(?<!\\)\|", lines[i].strip()[1:-1])])
                i += 1
            head, body = rows[0], rows[1:]
            out.append('<div class="table"><table><thead><tr>' +
                       "".join(f"<th>{inline(c)}</th>" for c in head) +
                       "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c.replace(chr(92) + '|', '|'))}</td>"
                                                for c in r) + "</tr>" for r in body) +
                       "</tbody></table></div>")
        elif re.match(r"[-*] ", line):
            items = []
            while i < len(lines) and (re.match(r"[-*] ", lines[i]) or
                                      (lines[i].startswith("  ") and items)):
                if re.match(r"[-*] ", lines[i]):
                    items.append(lines[i][2:])
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ul>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"(#{1,4} |```|\||[-*] )", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out), toc


# ---- the examples ------------------------------------------------------------------
class Example:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.name = path.stem
        text = path.read_text()
        # The first line is the title, `%% <title>'; the comment under it, the
        # description, a paragraph per run of lines.
        first, _, rest = text.partition("\n")
        if not first.startswith("%% "):
            sys.exit(f"{path.relative_to(ROOT)}: the first line is not its title, `%% <title>'")
        self.title = first[3:].strip()
        head = []
        for line in rest.splitlines():
            if not line.startswith("%"):
                break
            head.append(line[1:].strip())
        self.body = "\n".join(rest.splitlines()[len(head):]).lstrip("\n")
        paras, cur = [], []
        for line in head + [""]:
            if line:
                cur.append(line)
            elif cur:
                paras.append(" ".join(cur))
                cur = []
        self.paras = paras
        m = re.search(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", text, re.S)
        self.picture = m.group() if m else text
        self.number = self.name.partition("-")[0]
        first = paras[0] if paras else ""
        lead = re.split(r"(?<=[.:])\s|\s--\s", first, maxsplit=1)[0]
        self.lead = lead.rstrip(".:")
        self.svg = ROOT / "tests" / "reference" / f"{self.name}.svg"


# The examples in order, from single tensors up to two-dimensional networks:
# the number each section starts at. Every example falls in one
# (tests/test_pages.py).
SECTIONS = [(0, "The theme"),
            (1, "Single tensors and decompositions"),
            (6, "Matrix product states"),
            (13, "Algorithms on a chain"),
            (19, "Trees and MERA"),
            (21, "Two dimensions"),
            (26, "Quantum circuits")]


def section(ex: "Example") -> str:
    return [title for start, title in SECTIONS if int(ex.number) >= start][-1]


def examples() -> list[Example]:
    return [Example(p) for p in sorted((ROOT / "examples").glob("*.tex"))]


# ---- pages ---------------------------------------------------------------------------
def page(title: str, here: str, body: str, depth: int = 0) -> str:
    up = "../" * depth
    nav = "".join(
        f'<a href="{up}{href}"{" aria-current=page" if href == here or (href == "api.html" and here in REF_HTML) else ""}>{label}</a>'
        for href, label in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · tikz-tensors</title>
<link rel="stylesheet" href="{up}assets/theme.css">
<link rel="stylesheet" href="{up}assets/site.css">
<meta name="tt-root" content="{up}">
<script>try{{const t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<header class="top">
  <a class="brand" href="{up}index.html">tikz-tensors <span class="ver">v{version.version()}</span></a>
  <nav>{nav}<a href="{REPO}">GitHub</a></nav>
  <select class="versions" aria-label="Version" hidden></select>
  <button class="mode" type="button" aria-label="Switch light or dark"
    onclick="const r=document.documentElement,d=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);r.dataset.theme=d?'light':'dark';try{{localStorage.setItem('theme',r.dataset.theme)}}catch(e){{}}">◐</button>
</header>
<main>
{body}
</main>
<script>
/* The versions published beside this one (scripts/publish.py writes
   versions.json next to them); hidden where there is none -- a local build,
   a preview. Switching keeps the page. */
(() => {{
  const root = new URL("{up}", location.href);
  const here = root.pathname.split("/").filter(Boolean).pop();
  fetch(new URL("../versions.json", root)).then(r => r.ok ? r.json() : Promise.reject())
    .then(versions => {{
      const s = document.querySelector(".versions");
      if (!versions.includes(here)) return;
      for (const v of versions) s.add(new Option(v, v, false, v === here));
      s.hidden = false;
      s.onchange = () => {{
        const rest = location.href.slice(root.href.length);
        location.href = new URL("../" + s.value + "/" + rest, root).href;
      }};
    }}).catch(() => {{}});
}})();
</script>
<script>{TRACE_JS}{LIVE_JS if LIVE else ""}</script>
<footer>tikz-tensors v{version.version()} · <a href="{REPO}">source</a> ·
<a href="{REPO}/blob/main/CHANGELOG.md">changelog</a></footer>
</body>
</html>
"""


TRACE_JS = """
/* A line of code and what it drew light up together (traced_figure). */
document.querySelectorAll(".traced").forEach(box => {
  const all = n => box.querySelectorAll(`[data-line="${n}"]`);
  box.querySelectorAll("[data-line]").forEach(el => {
    const n = el.dataset.line;
    if (!box.querySelector(`.hl[data-line="${n}"]`)) return;
    el.classList.add("live");
    el.addEventListener("mouseenter", () => all(n).forEach(x => x.classList.add("lit")));
    el.addEventListener("mouseleave", () => all(n).forEach(x => x.classList.remove("lit")));
  });
});
"""


def figure(ex: Example, up: str) -> str:
    m = re.search(r'width="([\d.]+)', ex.svg.read_text()[:400])
    width = f' style="width:{float(m.group(1)) * 1.5:.0f}pt"' if m else ""
    return (f'<figure class="paper"><img{width} src="{up}figures/{ex.name}.svg" '
            f'alt="{html.escape(ex.title)}: {html.escape(ex.lead)}"></figure>')


# ---- what a line draws ------------------------------------------------------------
# Each reference picture has a trace beside it, tests/reference/<name>.json
# (tex/core/tikz-tensors-trace.tex, tests/compare.py): every tensor, label and
# index it draws, with the line of its file that drew it. A figure drawn here
# carries them as invisible shapes over the picture, and each line of its code
# the line it is in the file; pointing at either lights up both (TRACE_JS).
BP = 72 / 72.27   # TeX's pt in the SVG's units, PostScript points


def lines_of(code: str, source: str) -> list[int]:
    """The line of <source> (from 1) that each line of <code> is, in order; 0
    for one that is not in it."""
    src, out, k = source.splitlines(), [], 0
    for line in code.splitlines():
        j = next((j for j in range(k, len(src)) if src[j] == line), None)
        out.append(j + 1 if j is not None else 0)
        k = j + 1 if j is not None else k
    return out


def traced_code(code: str, source: str, up: str | None, added: frozenset = frozenset()) -> str:
    """LaTeX source as HTML a line at a time, each line tagged with its line in
    the file (data-line), the lines numbered in <added> marked as new."""
    rows = []
    for k, (line, n) in enumerate(zip(code.splitlines(), lines_of(code, source))):
        cls = "ln add" if k in added else "ln"
        tag = f' data-line="{n}"' if n else ""
        rows.append(f'<span class="{cls}"{tag}>{latex(line, up) or " "}</span>')
    return "".join(rows)


def traced_figure(name: str, up: str, scale: float, alt: str) -> str:
    """The picture tests/reference/<name>.svg at <scale>, with what each line
    of its file drew laid over it, unseen until that line is pointed at."""
    svg = (ROOT / "tests" / "reference" / f"{name}.svg").read_text()[:400]
    w, h = (float(x) for x in re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
    img = (f'<img style="width:{w * scale:.0f}pt" src="{up}figures/{name}.svg" '
           f'alt="{html.escape(alt)}">')
    kept = ROOT / "tests" / "reference" / f"{name}.json"
    if not kept.is_file():
        return f'<figure class="paper">{img}</figure>'
    data = json.loads(kept.read_text())
    x0, y0, x1, y1 = data["frame"]
    bx, by = (w - (x1 - x0) * BP) / 2, (h - (y1 - y0) * BP) / 2

    def at(x, y):
        return f"{(x - x0) * BP + bx:.2f},{(y1 - y) * BP + by:.2f}"
    shapes = []
    for line, kind, *nums in data["items"]:
        if kind == "p":
            pts = " ".join(at(nums[i], nums[i + 1]) for i in range(0, len(nums), 2))
            shapes.append(f'<polyline class="hl" data-line="{line}" points="{pts}"/>')
        else:
            a, b = at(nums[0], nums[3]), at(nums[2], nums[1])
            (ax, ay), (bx2, by2) = (map(float, a.split(",")), map(float, b.split(",")))
            shapes.append(f'<rect class="hl" data-line="{line}" x="{ax - 1:.2f}" y="{ay - 1:.2f}" '
                          f'width="{bx2 - ax + 2:.2f}" height="{by2 - ay + 2:.2f}" rx="2"/>')
    return (f'<figure class="paper"><span class="stage">{img}'
            f'<svg class="trace" viewBox="0 0 {w} {h}" aria-hidden="true">{"".join(shapes)}</svg>'
            f'</span></figure>')


# ---- drawn in the reader's browser ---------------------------------------------------
# With the engine fetched (scripts/engine.py: TikZJax, TeX in WebAssembly), the
# site carries it in live/ with the package's files beside it, and a figure can
# be edited on its page and drawn again where it is: `Edit live' on an
# example, and the playground (live.html). The engine loads on the first edit,
# not with the page. Without it the site is the same, less those two.
ENGINE = ROOT / ".engine"
LIVE = False
LIVE_BUTTON = '<button class="pill live-btn" type="button">Edit live</button>'
# What every live figure is drawn with: the examples' preamble, so that a
# figure is the file it is on the page.
LIVE_PACKAGES = '{"amsmath":"","amssymb":"","tikz-tensors":""}'


def copy_engine(out: pathlib.Path) -> bool:
    """The engine and the package's files, gzipped as it fetches them, into
    <out>/live/; False if the engine has not been fetched."""
    if not (ENGINE / "tikzjax.js").is_file():
        return False
    shutil.copytree(ENGINE, out / "live", ignore=shutil.ignore_patterns("VERSION"))
    files = sorted((ROOT / "tex").rglob("*.tex")) + [ROOT / "tex" / "tikz-tensors.sty",
                                                     ROOT / "examples" / "conventions" / "notation.tex"]
    for f in files:
        (out / "live" / "tex_files" / f"{f.name}.gz").write_bytes(gzip.compress(f.read_bytes(), mtime=0))
    return True


LIVE_JS = r"""
/* Live figures (scripts/engine.py). TikZJax turns a <script type="text/tikz">
   into an SVG; TeX's own messages come through console.log, which is how a
   mistake in the code is told from a figure still being drawn. */
const TT = (() => {
  const root = document.querySelector('meta[name="tt-root"]').content;
  let engine = null, log = [];
  const say = console.log.bind(console);
  console.log = (...a) => { log.push(a.join(" ")); say(...a); };
  function load() {
    if (!engine) engine = new Promise(done => {
      const l = document.createElement("link");
      l.rel = "stylesheet"; l.href = root + "live/fonts.css"; document.head.append(l);
      const s = document.createElement("script");
      s.src = root + "live/tikzjax.js"; s.onload = done; document.head.append(s);
    });
    return engine;
  }
  function draw(code, out, status) {
    const t0 = performance.now(), mine = {};
    out.dataset.turn = String(Number(out.dataset.turn || 0) + 1);
    const turn = out.dataset.turn;
    status.hidden = false; status.className = "small live-status";
    status.textContent = engine ? "Drawing…" : "Loading TeX into the page (once)…";
    load().then(() => {
      if (out.dataset.turn !== turn) return;
      log = [];
      const s = document.createElement("script");
      s.type = "text/tikz";
      s.dataset.texPackages = %s;
      s.dataset.addToPreamble = "\\input{notation.tex}";
      s.dataset.showConsole = "true";
      s.textContent = code;
      out.replaceChildren(s);
      const watch = setInterval(() => {
        if (out.dataset.turn !== turn) return clearInterval(watch);
        const svg = out.querySelector("svg");
        const bad = log.findIndex(l => /^! /.test(l));
        if (bad >= 0) {
          clearInterval(watch);
          const at = log.slice(bad).find(l => /^l\.\d+/.test(l)) || "";
          status.className = "small live-status bad";
          status.textContent = "TeX stopped: " + log[bad].slice(2) + (at ? "  (" + at.split(" ")[0] + " of the picture)" : "");
        } else if (svg && svg.querySelectorAll("path,use,text").length > 2) {
          clearInterval(watch);
          /* at the size the site shows its pictures, half again TeX's */
          svg.style.width = (parseFloat(svg.getAttribute("width")) * 1.5) + "pt";
          svg.style.height = "auto";
          status.textContent = "Drawn in your browser in " + ((performance.now() - t0) / 1000).toFixed(1) + " s.";
        }
      }, 200);
    });
  }
  return {draw};
})();

/* `Edit live' on an example: the code becomes editable and the figure is
   drawn again, a moment after the typing stops. */
document.querySelectorAll(".live-btn").forEach(btn => {
  const main = btn.closest("main");
  const area = main.querySelector("textarea.live-code");
  const status = main.querySelector(".live-status");
  const fig = main.querySelector(".traced figure.paper");
  let timer = null;
  btn.addEventListener("click", () => {
    const box = main.querySelector(".traced");
    box.classList.remove("traced");
    box.querySelectorAll("svg.trace").forEach(s => s.remove());
    area.previousElementSibling.previousElementSibling.hidden = true;  /* the hint */
    area.previousElementSibling.hidden = true;                         /* the code */
    area.hidden = false; area.rows = area.value.split("\n").length + 1;
    btn.hidden = true;
    const out = document.createElement("div");
    out.className = "live-out";
    fig.replaceChildren(out);
    TT.draw(area.value, out, status);
    area.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => TT.draw(area.value, out, status), 900);
    });
  });
});

/* The playground. */
const pg = document.querySelector(".playground");
if (pg) {
  const area = pg.querySelector("textarea"), out = pg.querySelector(".live-out");
  const status = pg.querySelector(".live-status"), pick = pg.querySelector("select");
  const pictures = JSON.parse(document.getElementById("tt-pictures").textContent);
  let timer = null;
  const start = location.hash.slice(1) in pictures ? location.hash.slice(1) : pick.value;
  pick.value = start; area.value = pictures[start];
  pick.addEventListener("change", () => {
    area.value = pictures[pick.value]; history.replaceState(null, "", "#" + pick.value);
    TT.draw(area.value, out, status);
  });
  area.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => TT.draw(area.value, out, status), 900);
  });
  TT.draw(area.value, out, status);
}
""" % json.dumps(LIVE_PACKAGES)


def live_page(exs: list[Example]) -> str:
    if not LIVE:
        body = """<h1>Playground</h1>
<p>This build of the site was made without the in-browser TeX
(<code>python3 scripts/engine.py</code> fetches it), so there is nothing to draw
with here. The published site has it.</p>"""
        return page("Playground", "live.html", body)
    pictures = {e.name: e.picture for e in exs if e.name != "00-palette"}
    data = json.dumps(pictures).replace("</", "<\\/")  # never closes the script
    options = "".join(f'<option value="{e.name}">{e.number} {html.escape(e.title)}</option>'
                      for e in exs if e.name in pictures)
    body = f"""<h1>Playground</h1>
<p>Write a figure and see it drawn, by TeX running in this page: the package
and the examples' notation (<a href="notation.html">canl, center, gate, ...</a>)
are loaded, so a tikzpicture of the <a href="api.html">reference</a>'s commands
is all a figure needs. Nothing is installed and nothing leaves your browser.
The first drawing loads TeX into the page, a few megabytes; each one after it
takes a few seconds.</p>
<div class="playground">
<p><label>Start from an example: <select>{options}</select></label></p>
<div class="split">
<textarea class="live-code" spellcheck="false" rows="22"></textarea>
<div><figure class="paper"><div class="live-out"></div></figure>
<p class="small live-status" hidden></p></div>
</div>
</div>
<script type="application/json" id="tt-pictures">{data}</script>
<p class="small">Drawn by <a href="https://github.com/drgrice1/tikzjax">TikZJax</a>
(GPL-3.0-or-later), TeX compiled to WebAssembly, served unmodified; the
pictures elsewhere on this site are the ones the tests check, drawn by
LuaLaTeX.</p>"""
    return page("Playground", "live.html", body)


def index_page(exs: list[Example]) -> str:
    gallery = ""
    for _, title in SECTIONS[1:]:
        cards = "".join(
            f'<a class="card" href="examples/{e.name}.html">{figure(e, "")}'
            f'<span class="num">{e.number}</span> {html.escape(e.title)}</a>'
            for e in exs if section(e) == title)
        gallery += f'<h3>{html.escape(title)}</h3><div class="gallery">{cards}</div>'

    shown = next(e for e in exs if e.name == "08-canonical")
    body = f"""<section class="hero">
<h1>tikz-tensors</h1>
<p>One TikZ format for <strong>tensor-network diagrams</strong>. A figure says
which tensors there are and how they are contracted; the package decides every
length and every coordinate, so two people who draw the same network write the
same file.</p>
</section>
<section class="split">
<div>
<h2>A figure</h2>
<p>A stack of layers, filled slot by slot, connected, and its open indices
labelled. No number in it is a length.</p>
<pre class="code">{latex(shown.body, "")}</pre>
</div>
<div>
<h2>Its picture</h2>
{figure(shown, "")}
<p class="small">The file is <a href="examples/{shown.name}.html">example
{shown.number}</a>, without its comment.</p>
<p class="small">The styles <code>canl</code>, <code>center</code>,
<code>canr</code>, <code>gauge</code> come from the
<a href="notation.html">notation</a>, which is the user's; the package draws
shapes only.</p>
</div>
</section>
<section>
<h2>Install</h2>
<p>Put <code>tex/</code> on TeX's search path —
<code>TEXINPUTS=/path/to/tikz-tensors/tex//:</code> — and
<code>\\usepackage{{tikz-tensors}}</code>. The <a href="api.html">reference</a>
lists the whole interface; every example below shows its code.</p>
</section>
<section>
<h2>Examples</h2>
{gallery}
</section>"""
    return page("Overview", "index.html", body)


def examples_page(exs: list[Example]) -> str:
    groups = ""
    for _, title in SECTIONS:
        rows = "".join(
            f'<li><a href="examples/{e.name}.html"><span class="num">{e.number}</span> '
            f'{html.escape(e.title)}</a><span class="lead">'
            f'{html.escape(prose(e.lead), quote=False)}</span></li>'
            for e in exs if section(e) == title)
        if rows:
            groups += f'<h2>{html.escape(title)}</h2><ul class="list">{rows}</ul>'
    body = f"""<h1>Examples</h1>
<p>Each one draws one object an algorithm uses and is named for that object,
in order from single tensors up to two-dimensional networks. Every page shows
the file as it is in <code>examples/</code> and the picture CI checks it
draws.</p>
{groups}"""
    return page("Examples", "examples.html", body)


def example_page(exs: list[Example], i: int) -> str:
    e = exs[i]
    prev = (f'<a href="{exs[i - 1].name}.html">← {html.escape(exs[i - 1].title)}</a>'
            if i > 0 else "<span></span>")
    nxt = (f'<a href="{exs[i + 1].name}.html">{html.escape(exs[i + 1].title)} →</a>'
           if i + 1 < len(exs) else "<span></span>")
    text = "".join(f"<p>{autolink(html.escape(prose(p), quote=False))}</p>" for p in e.paras)
    source = e.path.read_text()
    body = f"""<p class="crumb"><a href="../examples.html">Examples</a> / {e.number}</p>
<h1>{html.escape(e.title)}</h1>
<div class="traced">
{traced_figure(e.name, "../", 1.5, f"{e.title}: {e.lead}")}
<div class="split">
<div class="prose">{text}</div>
<div>
<h2 class="with-button">The picture{LIVE_BUTTON if LIVE else ""}</h2>
<p class="small hint">Point at a line to see what it draws, or at the picture to see which line drew it.</p>
<pre class="code">{traced_code(e.picture, source, "../")}</pre>
<textarea class="live-code" spellcheck="false" hidden>{html.escape(e.picture)}</textarea>
<p class="small live-status" hidden></p>
<details><summary>The whole file</summary>
<pre class="code">{traced_code(e.body, source, "../")}</pre></details>
<p class="small"><a href="{REPO}/blob/main/examples/{e.name}.tex">examples/{e.name}.tex</a></p>
</div>
</div>
</div>
<nav class="pager">{prev}{nxt}</nav>"""
    return page(e.title, "examples.html", body, depth=1)


def defined_in() -> dict[str, str]:
    """Each public command and style, and the file under tex/ that defines it."""
    where = {}
    for path in sorted((ROOT / "tex").rglob("*.tex")) + [ROOT / "tex" / "tikz-tensors.sty"]:
        text = path.read_text()
        rel = path.relative_to(ROOT).as_posix()
        for name in re.findall(r"\\newcommand\{(\\tn[a-z]+)\}", text):
            where[name] = rel
        for name in re.findall(r"(?<![\w-])(tn [a-z ]+?)/\.(?!append)", text):
            where.setdefault(name, rel)
    return where


def definition(name: str) -> str:
    """The keys that define the style <name>, as tex/ writes them."""
    out = []
    for path in sorted((ROOT / "tex").rglob("*.tex")):
        text = path.read_text()
        for m in re.finditer(rf"(?<![\w-]){re.escape(name)}/\.(?!append)([a-z ]+?)\s*=\s*", text):
            k, depth = m.end(), 0
            while k < len(text):
                c = text[k]
                if c == "{":
                    depth += 1
                elif c == "}":
                    if depth == 0:
                        break
                    depth -= 1
                    if depth == 0:
                        k += 1
                        break
                elif c in ",\n" and depth == 0:
                    break
                k += 1
            value = re.sub(r"\s*\n\s*", " ", text[m.end():k].strip())
            out.append(f"{name}/.{m.group(1)} = {value}")
    return "\n".join(out)


class Picture:
    """A picture of the styles page, docs/reference/styles/<name>.tex: its
    title, its description, and the part of it worth reading."""
    def __init__(self, path: pathlib.Path):
        text = path.read_text()
        self.name = path.stem
        self.path = path.relative_to(ROOT).as_posix()
        self.svg = ROOT / "tests" / "reference" / f"{self.name}.svg"
        head = []
        for line in text.splitlines()[1:]:
            if not line.startswith("%"):
                break
            head.append(line[1:].strip())
        self.paras = [" ".join(p.split()) for p in "\n".join(head).split("\n\n") if p.strip()]
        pre = text.split(r"\usepackage{tikz-tensors}", 1)[1].split(r"\begin{document}", 1)[0]
        pic = re.search(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", text, re.S).group()
        self.code = (pre.strip() + "\n" if pre.strip() else "") + pic


def pictured(body: str) -> tuple[str, str]:
    """An entry's Markdown without the line that names its picture, and the
    picture: its description, the drawing, and the code that drew it."""
    line = re.search(r"(?m)^\[[^\]]*\]\((styles/[a-z-]+\.tex)\)\s*$", body)
    if not line:
        return body, ""
    pic = Picture(REFERENCE / line.group(1))
    if not pic.svg.exists():
        sys.exit(f"{pic.svg.relative_to(ROOT)}: no reference picture for {pic.path}")
    text = "".join(f"<p>{autolink(html.escape(prose(t), quote=False))}</p>" for t in pic.paras)
    source = (ROOT / pic.path).read_text()
    return body.replace(line.group(), ""), (
        f'{text}<div class="traced">'
        f'{traced_figure(pic.name, "", 1.5, pic.paras[0] if pic.paras else pic.name)}'
        f'<p class="def-head">Drawn by <a href="{REPO}/blob/main/{pic.path}">{pic.path}</a></p>'
        f'<pre class="code">{traced_code(pic.code, source, "")}</pre></div>')


def walkthrough() -> str:
    """docs/reference/steps/step-<n>.tex in order: each step's code, what it
    adds to the step before marked, beside the picture it draws."""
    out, before = [], []
    paths = sorted((REFERENCE / "steps").glob("step-*.tex"), key=lambda p: int(p.stem[5:]))
    for n, path in enumerate(paths, 1):
        pic = Picture(path)
        if not pic.svg.exists():
            sys.exit(f"{pic.svg.relative_to(ROOT)}: no reference picture for {pic.path}")
        title = path.read_text().partition("\n")[0][3:].strip()
        code = re.search(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
                         path.read_text(), re.S).group()
        lines = code.splitlines()
        added = set()
        for tag, _, _, j1, j2 in difflib.SequenceMatcher(None, before, lines).get_opcodes():
            if tag in ("insert", "replace"):
                added.update(range(j1, j2))
        before = lines
        m = re.search(r'width="([\d.]+)', pic.svg.read_text()[:400])
        # a picture too wide to read at half the card goes under its code
        wide = " wide" if m and float(m.group(1)) > 260 else ""
        text = "".join(f"<p>{autolink(html.escape(prose(t), quote=False))}</p>" for t in pic.paras)
        out.append(
            f'<article class="doc step" id="step-{n}"><header><div class="sigs">'
            f'<span class="sig">Step {n}. {html.escape(title)}</span></div>'
            f'<a class="src" href="{REPO}/blob/main/{pic.path}">‹/› source</a></header>'
            f'<div class="doc-body">{text}<div class="pair traced{wide}">'
            f'<pre class="code diff">{traced_code(code, path.read_text(), "", frozenset(added))}</pre>'
            f'{traced_figure(pic.name, "", 1.3, title)}</div></div></article>')
    return "".join(out)


def reference_page(md: str, here: str, title: str) -> str:
    """A page of docs/reference/: its prose as it is, and each `###' entry --
    a command, a group of styles -- a card of its own: the names on top with
    a button to the source that defines them, then what it is, its keys, and
    for a style its definition and a picture."""
    text = (REFERENCE / md).read_text()
    where = defined_in()
    parts, toc = [], []
    for part in re.split(r"(?m)^(?=#{2,3} )", text):
        if not part.startswith("### "):
            marker = re.search(r"(?m)^\[[^\]]*\]\(steps/\)\s*$", part)
            if marker:
                head_html, t = markdown(part[:marker.start()])
                tail_html, t2 = markdown(part[marker.end():])
                parts.append(head_html + walkthrough() + tail_html)
                toc += t + t2
                continue
            body, t = markdown(part)
            parts.append(body)
            toc += t
            continue
        head, _, rest = part.partition("\n")
        sigs = re.findall(r"`([^`]+)`", head)
        names = [n for sig in sigs for n in re.findall(r"\\tn[a-z]+|^tn [a-z ]+$", sig)]
        if names and names[0].startswith("\\"):
            kind, ident = "Command", names[0][1:]
        elif names:
            kind, ident = "Style", slug(names[0])
        else:
            kind, ident = "", slug(head[4:])
        label = (", ".join(f"<code>{html.escape(n)}</code>" for n in names)
                 or inline(head[4:]))
        toc.append((3, ident, label))
        rest, picture = pictured(rest)
        body, _ = markdown(rest)
        body += picture
        if kind == "Style":
            defs = "\n".join(definition(n) for n in names)
            body += (f'<p class="def-head">Defined as</p>'
                     f'<pre class="code">{latex(defs, "")}</pre>')
        src = where.get(names[0]) if names else None
        source = f'<a class="src" href="{REPO}/blob/main/{src}">‹/› source</a>' if src else ""
        if kind == "Command":
            lines = "".join(f'<code class="sig">{latex(sig)}</code>' for sig in sigs)
        elif kind == "Style":
            lines = ('<code class="sig">'
                     + ", ".join(html.escape(n) for n in names) + "</code>")
        else:
            lines = f'<span class="sig">{inline(head[4:])}</span>'
        badge = f'<span class="kind">{kind}</span>' if kind else ""
        parts.append(
            f'<article class="doc" id="{ident}"><header>'
            f'<div class="sigs">{lines}</div>{badge}{source}'
            f'</header><div class="doc-body">{body}</div></article>')
    contents = "".join(f'<li class="l{lvl}"><a href="#{ident}">{text}</a></li>'
                       for lvl, ident, text in toc if lvl in (2, 3))
    tabs = "".join(f'<a href="{h}"{" aria-current=page" if h == here else ""}>{t}</a>'
                   for _, h, t in REF_PAGES)
    return page(title, here,
                f'<nav class="tabs">{tabs}</nav>'
                f'<div class="with-toc"><aside><ul class="toc">{contents}</ul></aside>'
                f'<article>{"".join(parts)}</article></div>')


def notation_page() -> str:
    path = ROOT / "examples" / "conventions" / "notation.tex"
    text = path.read_text()
    body = f"""<h1>Notation</h1>
<p>The package names shapes and lines, never meanings. What a shape stands for
is a notation, and a notation belongs to whoever draws in it: a file of styles
named for the meaning, built from the package's shapes, loaded after the
package. This is the one the examples are drawn in. Yours can be different and
every figure keeps working.</p>
<pre class="code">{latex(text, "")}</pre>
<p class="small"><a href="{REPO}/blob/main/examples/conventions/notation.tex">examples/conventions/notation.tex</a></p>"""
    return page("Notation", "notation.html", body)


CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
code,pre{font:13.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
code{background:var(--soft);padding:.1em .35em;border-radius:4px}
.top{position:sticky;top:0;z-index:1;display:flex;align-items:center;gap:20px;
  padding:10px 24px;background:var(--card);border-bottom:1px solid var(--line)}
.brand{font-weight:650;color:var(--fg)}
.ver{font-weight:400;color:var(--muted);font-size:13px}
.top nav{display:flex;gap:16px;flex-wrap:wrap;flex:1}
.top nav a{color:var(--muted)}
.top nav a[aria-current]{color:var(--fg);font-weight:600}
.versions{background:var(--card);color:var(--fg);border:1px solid var(--line);
  border-radius:6px;padding:2px 6px;font:inherit;font-size:14px}
.mode{background:none;border:1px solid var(--line);border-radius:6px;color:var(--fg);
  cursor:pointer;padding:2px 8px;font-size:16px}
main{max-width:1120px;margin:0 auto;padding:24px}
footer{max-width:1120px;margin:0 auto;padding:24px;color:var(--muted);font-size:14px;
  border-top:1px solid var(--line)}
h1{font-size:30px;line-height:1.25;margin:.3em 0 .4em}
h2{font-size:21px;margin:1.4em 0 .5em}
h3{font-size:17px;margin:1.6em 0 .4em}
.hero p{font-size:18px;max-width:46em;color:var(--fg)}
.small{font-size:14px;color:var(--muted)}
.split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start}
@media (max-width:820px){.split,.with-toc{grid-template-columns:minmax(0,1fr)!important}
  .with-toc aside{display:none}}
pre.code{background:var(--card);border:1px solid var(--line);border-radius:8px;
  padding:12px 14px;overflow-x:auto;margin:.6em 0}
.tx-comment{color:var(--muted);font-style:italic}
.tx-math{color:var(--green5)}
.tx-cmd{color:var(--accent)}
.tx-brace{color:var(--warm4)}
a.ref{color:inherit;text-decoration:none;border-bottom:1px dotted var(--line)}
a.ref:hover{border-bottom-color:var(--accent);text-decoration:none}
:root[data-theme=dark] .tx-math{color:var(--green3)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .tx-math{color:var(--green3)}}
figure.paper{margin:12px 0;padding:16px;background:#fff;border:1px solid var(--line);
  border-radius:8px;text-align:center;overflow-x:auto}
figure.paper img{max-width:100%;height:auto}
.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.card{display:block;color:var(--fg);background:var(--card);border:1px solid var(--line);
  border-radius:10px;padding:10px 12px 12px;font-weight:550}
.card:hover{border-color:var(--accent);text-decoration:none}
.card figure.paper{margin:0 0 8px;padding:8px;height:150px;display:flex;
  align-items:center;justify-content:center}
.card figure.paper img{max-height:130px;width:auto!important}
.num{color:var(--muted);font-variant-numeric:tabular-nums;font-weight:400;margin-right:4px}
.list{list-style:none;padding:0}
.list li{padding:10px 0;border-bottom:1px solid var(--line);display:grid;
  grid-template-columns:minmax(200px,280px) 1fr;gap:16px}
.lead{color:var(--muted);font-size:15px}
.crumb{color:var(--muted);margin:0}
.prose p{margin:.2em 0 .9em}
details{margin:.6em 0}
summary{cursor:pointer;color:var(--muted)}
.pager{display:flex;justify-content:space-between;margin-top:32px;padding-top:16px;
  border-top:1px solid var(--line)}
.with-toc{display:grid;grid-template-columns:220px minmax(0,1fr);gap:32px}
.with-toc aside{position:sticky;top:64px;align-self:start;max-height:calc(100vh - 80px);
  overflow:auto}
.toc{list-style:none;padding:0;margin:0;font-size:14px}
.toc li{margin:2px 0}
.toc .l3{padding-left:12px}
.toc a{color:var(--muted)}
.table{overflow-x:auto}
table{border-collapse:collapse;margin:.6em 0;font-size:15px}
td:first-child code{white-space:nowrap}
.toc code{background:none;padding:0;color:inherit}
article.doc{background:var(--card);border:1px solid color-mix(in srgb,var(--fg) 24%,transparent);
  border-radius:12px;margin:24px 0;padding:14px 18px 10px;scroll-margin-top:64px;
  box-shadow:0 1px 4px color-mix(in srgb,var(--fg) 12%,transparent)}
article.doc:target{box-shadow:0 0 0 2px var(--accent)}
article.doc>header{display:flex;align-items:center;flex-wrap:wrap;gap:6px 10px;
  padding-bottom:10px;border-bottom:1px solid color-mix(in srgb,var(--fg) 18%,transparent)}
article.doc .sigs{flex:1;display:flex;flex-direction:column;gap:2px;min-width:0}
code.sig{background:none;padding:0;font-size:15px;font-weight:600;overflow-wrap:anywhere}
article.doc .kind{font-size:12px;color:var(--accent);border:1px solid var(--accent);
  border-radius:999px;padding:0 8px;white-space:nowrap}
article.doc .src{font-size:12px;color:var(--fg);background:var(--soft);white-space:nowrap;
  border:1px solid color-mix(in srgb,var(--fg) 22%,transparent);border-radius:999px;padding:1px 10px}
article.doc .src:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}
article.doc .doc-body>p:first-child{margin-top:.7em}
article.doc .doc-body table{width:100%}
article.doc .doc-body td:first-child{width:38%}
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--line);margin:0 0 20px}
.tabs a{padding:6px 14px;color:var(--muted);border-bottom:2px solid transparent;margin-bottom:-1px}
.tabs a[aria-current]{color:var(--fg);font-weight:600;border-bottom-color:var(--accent)}
.tabs a:hover{text-decoration:none;color:var(--fg)}
.def-head{margin:.8em 0 0;font-size:14px;color:var(--muted)}
span.sig{font-weight:600}
pre.code .ln{display:block}
pre.code .ln.live{cursor:default}
pre.code .ln.lit{background:color-mix(in srgb,#cf222e 16%,transparent);
  box-shadow:inset 3px 0 #cf222e}
.hint{margin:-.2em 0 .4em}
h2.with-button{display:flex;align-items:center;gap:12px}
button.pill{font:inherit;font-size:13px;font-weight:400;cursor:pointer;color:var(--fg);
  background:var(--soft);border:1px solid color-mix(in srgb,var(--fg) 22%,transparent);
  border-radius:999px;padding:2px 12px}
button.pill:hover{border-color:var(--accent);color:var(--accent)}
textarea.live-code{width:100%;font:13.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  background:var(--card);color:var(--fg);border:1px solid var(--accent);border-radius:8px;
  padding:12px 14px;resize:vertical;tab-size:2}
.live-out{min-height:120px;display:flex;align-items:center;justify-content:center}
.live-out svg{max-width:100%;height:auto}
.live-status.bad{color:var(--bad);font-weight:600}
.playground select{font:inherit;background:var(--card);color:var(--fg);
  border:1px solid var(--line);border-radius:6px;padding:2px 6px}
.stage{position:relative;display:inline-block;max-width:100%}
.stage img{display:block;max-width:100%;height:auto}
svg.trace{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
svg.trace .hl{opacity:0;transition:opacity .12s}
svg.trace .hl.lit{opacity:1}
svg.trace rect.hl{fill:rgba(207,34,46,.16);stroke:#cf222e;stroke-width:1}
svg.trace polyline.hl{fill:none;stroke:#cf222e;stroke-width:2.4;stroke-linecap:round;
  stroke-linejoin:round;stroke-opacity:.8}
.pair{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;align-items:center}
.pair figure.paper{margin:.6em 0}
.pair.wide{grid-template-columns:minmax(0,1fr)}
@media (max-width:820px){.pair{grid-template-columns:minmax(0,1fr)}}
pre.diff{--diff:#cf222e;white-space:pre-wrap}
:root[data-theme=dark] pre.diff{--diff:#ff6b6b}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) pre.diff{--diff:#ff6b6b}}
pre.diff .ln{display:block;padding-left:18px;margin-left:-14px;text-indent:-2.2em;
  border-left:3px solid transparent}
pre.diff .ln{padding-left:calc(18px + 2.2em)}
pre.diff .ln.add{background:color-mix(in srgb,var(--diff) 15%,transparent);
  border-left-color:var(--diff)}
pre.diff .ln.add::before{content:"+";position:absolute;margin-left:-13px;text-indent:0;
  color:var(--diff);font-weight:700}
th,td{border-bottom:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}
"""


ANCHORS: dict[str, str] = {}


def build(out: pathlib.Path) -> list[str]:
    """Write the site to <out>; the pages written, relative to it."""
    if out.exists():
        shutil.rmtree(out)
    (out / "assets").mkdir(parents=True)
    (out / "figures").mkdir()
    (out / "examples").mkdir()
    shutil.copy(ROOT / "theme" / "theme.css", out / "assets" / "theme.css")
    (out / "assets" / "site.css").write_text(CSS)
    (out / ".nojekyll").write_text("")
    global LIVE
    LIVE = copy_engine(out)
    ANCHORS.clear()
    ANCHORS.update(api_anchors())
    exs = examples()
    for e in exs:
        if not e.svg.exists():
            sys.exit(f"{e.svg.relative_to(ROOT)}: no reference picture for {e.name}")
        shutil.copy(e.svg, out / "figures" / e.svg.name)
    for svg in sorted([*(ROOT / "tests" / "reference").glob("style-*.svg"),
                       *(ROOT / "tests" / "reference").glob("step-*.svg")]):
        shutil.copy(svg, out / "figures" / svg.name)
    pages = {"index.html": index_page(exs), "examples.html": examples_page(exs),
             "notation.html": notation_page(), "live.html": live_page(exs)}
    for md, html_name, title in REF_PAGES:
        pages[html_name] = reference_page(md, html_name, "Reference" if md == "index.md" else title)
    for i, e in enumerate(exs):
        pages[f"examples/{e.name}.html"] = example_page(exs, i)
    for name, text in pages.items():
        (out / name).write_text(text)
    return sorted(pages)


def main() -> int:
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
    pages = build(out)
    print(f"wrote {len(pages)} pages to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
