#!/usr/bin/env python3
"""Build the documentation site: the interface, and every example with its code.

    python3 scripts/pages.py [OUT]        # writes the site to OUT (default _site/)

Everything on it is read from the repository, so it cannot drift from it:

- the reference (`api.html`) is docs/api.md, the page tests/coverage.py holds
  to the code;
- each example page shows the file in examples/ and the picture in
  tests/reference/ that CI checks that file draws -- the code beside the
  picture is the code that drew it;
- the notation page is examples/conventions/notation.tex;
- the colours are theme/theme.css, the theme the diagrams are drawn in, light
  and dark.

No TeX is needed: the pictures are the committed references. Standard library
only. .github/workflows/pages.yml publishes the site from main, which is always
a release; tests/test_pages.py builds it and checks every link.
"""
from __future__ import annotations

import html
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = "https://github.com/pen-sotashimozono/tikz-tensors"
sys.path.insert(0, str(ROOT / "scripts"))
import version  # noqa: E402

NAV = [("index.html", "Overview"), ("examples.html", "Examples"),
       ("api.html", "Reference"), ("notation.html", "Notation")]


# ---- LaTeX, coloured -----------------------------------------------------------
TOKEN = re.compile(r"(?P<comment>(?<!\\)%.*)|(?P<math>(?<!\\)\$[^$\n]*\$)"
                   r"|(?P<cmd>\\(?:[A-Za-z@]+|.))|(?P<brace>[{}\[\]])")


def latex(code: str) -> str:
    """LaTeX source as HTML, with comments, math, commands and braces marked."""
    out, pos = [], 0
    for m in TOKEN.finditer(code):
        out.append(html.escape(code[pos:m.start()]))
        kind = m.lastgroup
        out.append(f'<span class="tx-{kind}">{html.escape(m.group())}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:]))
    return "".join(out)


# ---- Markdown, the subset docs/api.md uses ---------------------------------------
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


def link(target: str) -> str:
    """A link in the repository's own Markdown, as one that works on the site."""
    if re.match(r"[a-z]+:", target) or target.startswith("#"):
        return target
    return f"{REPO}/blob/main/{target.lstrip('./')}"


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>|\\", "", text.lower())).strip("-")


def markdown(text: str) -> tuple[str, list[tuple[int, str, str]]]:
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
            out.append(f'<pre class="code">{latex(chr(10).join(lines[i + 1:j]))}</pre>')
            i = j + 1
        elif m := re.match(r"(#{1,4}) (.*)", line):
            level, body = len(m.group(1)), inline(m.group(2))
            ident = slug(body)
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


def examples() -> list[Example]:
    return [Example(p) for p in sorted((ROOT / "examples").glob("*.tex"))]


# ---- pages ---------------------------------------------------------------------------
def page(title: str, here: str, body: str, depth: int = 0) -> str:
    up = "../" * depth
    nav = "".join(
        f'<a href="{up}{href}"{" aria-current=page" if href == here else ""}>{label}</a>'
        for href, label in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · tikz-tensors</title>
<link rel="stylesheet" href="{up}assets/theme.css">
<link rel="stylesheet" href="{up}assets/site.css">
<script>try{{const t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<header class="top">
  <a class="brand" href="{up}index.html">tikz-tensors <span class="ver">v{version.version()}</span></a>
  <nav>{nav}<a href="{REPO}">GitHub</a></nav>
  <button class="mode" type="button" aria-label="Switch light or dark"
    onclick="const r=document.documentElement,d=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);r.dataset.theme=d?'light':'dark';try{{localStorage.setItem('theme',r.dataset.theme)}}catch(e){{}}">◐</button>
</header>
<main>
{body}
</main>
<footer>tikz-tensors v{version.version()} · <a href="{REPO}">source</a> ·
<a href="{REPO}/blob/main/CHANGELOG.md">changelog</a></footer>
</body>
</html>
"""


def figure(ex: Example, up: str) -> str:
    m = re.search(r'width="([\d.]+)', ex.svg.read_text()[:400])
    width = f' style="width:{float(m.group(1)) * 1.5:.0f}pt"' if m else ""
    return (f'<figure class="paper"><img{width} src="{up}figures/{ex.name}.svg" '
            f'alt="{html.escape(ex.title)}: {html.escape(ex.lead)}"></figure>')


def index_page(exs: list[Example]) -> str:
    gallery = "".join(
        f'<a class="card" href="examples/{e.name}.html">{figure(e, "")}'
        f'<span class="num">{e.number}</span> {html.escape(e.title)}</a>'
        for e in exs if e.svg.exists() and e.name != "00-palette")
    shown = next(e for e in exs if e.name == "04-canonical")
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
<pre class="code">{latex(shown.body)}</pre>
</div>
<div>
<h2>Its picture</h2>
{figure(shown, "")}
<p class="small">The file is <a href="examples/{shown.name}.html">example
{shown.number}</a>, without its comment.</p>
<p class="small">The styles <code>canl</code>, <code>centre</code>,
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
<div class="gallery">{gallery}</div>
</section>"""
    return page("Overview", "index.html", body)


def examples_page(exs: list[Example]) -> str:
    rows = "".join(
        f'<li><a href="examples/{e.name}.html"><span class="num">{e.number}</span> '
        f'{html.escape(e.title)}</a><span class="lead">{html.escape(prose(e.lead), quote=False)}</span></li>'
        for e in exs)
    body = f"""<h1>Examples</h1>
<p>Each one draws one object an algorithm uses and is named for that object.
Every page shows the file as it is in <code>examples/</code> and the picture CI
checks it draws.</p>
<ul class="list">{rows}</ul>"""
    return page("Examples", "examples.html", body)


def example_page(exs: list[Example], i: int) -> str:
    e = exs[i]
    prev = (f'<a href="{exs[i - 1].name}.html">← {html.escape(exs[i - 1].title)}</a>'
            if i > 0 else "<span></span>")
    nxt = (f'<a href="{exs[i + 1].name}.html">{html.escape(exs[i + 1].title)} →</a>'
           if i + 1 < len(exs) else "<span></span>")
    text = "".join(f"<p>{html.escape(prose(p), quote=False)}</p>" for p in e.paras)
    body = f"""<p class="crumb"><a href="../examples.html">Examples</a> / {e.number}</p>
<h1>{html.escape(e.title)}</h1>
{figure(e, "../")}
<div class="split">
<div class="prose">{text}</div>
<div>
<h2>The picture</h2>
<pre class="code">{latex(e.picture)}</pre>
<details><summary>The whole file</summary>
<pre class="code">{latex(e.body)}</pre></details>
<p class="small"><a href="{REPO}/blob/main/examples/{e.name}.tex">examples/{e.name}.tex</a></p>
</div>
</div>
<nav class="pager">{prev}{nxt}</nav>"""
    return page(e.title, "examples.html", body, depth=1)


def api_page() -> str:
    body, toc = markdown((ROOT / "docs" / "api.md").read_text())
    def short(text):  # a command's heading by its names alone
        names = re.findall(r"\\tn[a-z]+", html.unescape(re.sub(r"<[^>]+>", "", text)))
        return ", ".join(f"<code>{n}</code>" for n in names) if names else text
    contents = "".join(f'<li class="l{lvl}"><a href="#{ident}">{short(text)}</a></li>'
                       for lvl, ident, text in toc if lvl in (2, 3))
    return page("Reference", "api.html",
                f'<div class="with-toc"><aside><ul class="toc">{contents}</ul></aside>'
                f'<article>{body}</article></div>')


def notation_page() -> str:
    path = ROOT / "examples" / "conventions" / "notation.tex"
    text = path.read_text()
    body = f"""<h1>Notation</h1>
<p>The package names shapes and lines, never meanings. What a shape stands for
is a notation, and a notation belongs to whoever draws in it: a file of styles
named for the meaning, built from the package's shapes, loaded after the
package. This is the one the examples are drawn in. Yours can be different and
every figure keeps working.</p>
<pre class="code">{latex(text)}</pre>
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
.tx-math{color:var(--green3)}
.tx-cmd{color:var(--accent)}
.tx-brace{color:var(--warm2)}
:root[data-theme=dark] .tx-math{color:var(--green1)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .tx-math{color:var(--green1)}}
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
th,td{border-bottom:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}
"""


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
    exs = examples()
    for e in exs:
        if not e.svg.exists():
            sys.exit(f"{e.svg.relative_to(ROOT)}: no reference picture for {e.name}")
        shutil.copy(e.svg, out / "figures" / e.svg.name)
    pages = {"index.html": index_page(exs), "examples.html": examples_page(exs),
             "api.html": api_page(), "notation.html": notation_page()}
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
