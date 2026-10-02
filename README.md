# tikz-tensors

One TikZ format for **tensor-network diagrams**, in one **shared theme** for
figures, notes and slides.

```latex
\usepackage{tikz-tensors}
```

| | |
|---|---|
| ![expansion](examples/out/01-expansion.svg) | ![swap](examples/out/02-swap.svg) |
| ![mps](examples/out/03-mps.svg) | |

## The notation

What a **leg** carries:

| style | drawn as | means |
|---|---|---|
| `cont` | wavy, electron colour | a continuous argument (**r**, **r**₁, x) |
| `disc` | plain line | a finite index (i, μ, a bond) |

What a **node** is:

| style | drawn as | means |
|---|---|---|
| `fn`, `fnwide`, `fntall` | circle / rounded box, electron colour | a function of position (ψ, φ) |
| `coef`, `coefwide`, `coeftall` | square / box, grey | an array of numbers (C, c, A) |
| `op`, `opwide` | square-cornered box, ink | an operator (Ĥ, an MPO) |
| `frame` | dashed box | nodes that contract to one object |

Joining two legs sums over that index. The expansion
ψ(**r**₁, **r**₂) = Σ C_ij φ_i(**r**₁) φ_j(**r**₂) is a `coefwide` C on two `fn` φ,
each with a `cont` leg: **the numbers sit on the basis functions, which sit on
space.** A finite-basis object (an MPS over occupation numbers) has no wavy legs.

A figure of an algorithm is drawn on a **stack**: n sites across and named
layers down, at one pitch the package owns, with an `env` (the rest of the
network, contracted) at either end. Nothing in it is a length or a coordinate:

```latex
\tnstack[left=$L$, right=$R$]{H}{2}{ket, op, bra}   % examples/06-heff-two-site.tex
\tnlayer{H}{op}{mpo/$W$, mpo/$W$}
\tnconnect{H}
\tnopen{up}{H-op-1, H-op-2}
```

`\tnlayer` takes one entry per slot: `<style>/<label>`, `<style>/<label>/<span>`
for a tensor across several, `.` for an empty slot, `-` for one the layer's
index runs through. `\tneq[$\lambda$]` writes an equals sign and the next
stack goes after it. `tests/lint.py` holds the examples to these rules
(`docs/roadmap.md`).

Exchanging two fermion legs: `\tnswap[cont|disc]{<left top>}{<right top>}{<drop>}`
draws the crossing (the sign goes in the equation, as in example 02).

Labels are ordinary LaTeX math, so a diagram uses exactly the glyphs of the
equations beside it; `pdftocairo -svg` turns them into paths, so the SVG shows
the same everywhere without the fonts installed.

## The theme

`theme/tokens.toml` is the only place a colour is defined: the GitHub-style
palette of the page (light and dark) and the **physics colours**, which carry
meaning in every medium — `ele` electrons and position legs, `nuc` nuclei,
`coef` arrays, `exchange` the exchange term / hole / sign, `exact` reference
results.

```sh
python3 scripts/theme.py           # writes tex/tikz-tensors-colors.tex and theme/theme.css
python3 scripts/theme.py --check   # fails if either is out of date
```

Standard library only (Python 3.11+). `theme/theme.css` defines every token as
a CSS custom property (`--fg`, `--accent`, `--ele`, …; dark under
`prefers-color-scheme` and `[data-theme="dark"]`), for HTML notes and
storyboards; the TeX file defines `tt<name>` for the page tokens and the
physics colours by name for diagrams.

## Use in a project

Put `tex/` on TeX's search path — for example
`TEXINPUTS=/path/to/tikz-tensors/tex//:` — or copy `tex/*` next to your
figures. A figure page is a `standalone` document:

```latex
\documentclass[border=4pt]{standalone}
\usepackage{amsmath}
\usepackage{tikz-tensors}
\begin{document}
\begin{tikzpicture}
  \node[fn] (p) at (0,0) {$\varphi$};
  \draw[cont] (p) -- ++(0,-1) node[leg, below] {$\mathbf r$};
  \draw[disc] (p) -- ++(-1,0) node[leg, left] {$i$};
\end{tikzpicture}
\end{document}
```

`scripts/build-examples.sh` builds `examples/*.tex` into `examples/out/`
(SVG and PDF) with LuaLaTeX and `pdftocairo`.

## Where the real tikz-tensors is

**`main` of this repository is the one canonical tikz-tensors, and it is
always a release**: its `tex/` and `theme/` are exactly the newest tag. Every
other copy is a pointer or a proposal.

A project uses it as a **git submodule** pinned at a release, and develops it
there, in place, while its own figures rebuild against the edit:

```text
project/.github/tools/figures/tikz-tensors   (submodule)
  pinned at v0.2.0                      -> the project builds with a release
  on branch <project>/<topic>, pushed   -> a proposal from that project; the
                                           project may build with it for a while
  PR to main, merged                    -> released as the next version; every
                                           project moves to it when it chooses
```

Name a development branch after the project it comes from
(`review-hfdmrg/fn-size`), so a branch says where it was born. Whether a
proposal goes to `main` is decided separately, as a PR here; until then it is
not tikz-tensors, only that project's variant of it.

Gates that keep this true:

- **`main` takes only pull requests** (ruleset: no direct push, no force push,
  no deletion, admins included), each with `version`, `theme` and `test`
  passing on a branch up to date with `main`.
- **The version check** (below) makes every change to the package a new
  version, so a merge to `main` is a release.
- **After each merge** the Release workflow tags and releases that version and
  confirms `main`'s package is exactly that tag (`version.py released`).
- A project's own CI can then tell a pinned release from a proposal, and a
  pushed commit from one that exists only on somebody's machine.

## Versions

[Semantic versioning](https://semver.org), on what a document can refer to:
the style names, the commands, the colour names and the theme tokens. The
version lives only in the `\ProvidesPackage` line of `tex/tikz-tensors.sty`
(so a document's `.log` shows it); `CHANGELOG.md` has one section per version.

| step | when |
|---|---|
| **major** | a name is removed or renamed, or changes meaning (`cont` no longer a continuous argument) |
| **minor** | a name is added, or a picture in `tests/reference/` changes — existing figures still compile but look different |
| **patch** | anything else under `tex/` or `theme/`: a fix that leaves every picture as it was |

Before 1.0.0 a removal is a minor step, as semver allows for 0.x (v0.2.0
removed the schematic parts). A change outside `tex/` and `theme/` (tests,
docs, CI) does not move the version.

```sh
python3 scripts/version.py                     # the current version
python3 scripts/version.py bump minor "Why."   # move it one step; opens the CHANGELOG entry
python3 scripts/version.py check --base origin/main
python3 scripts/version.py released origin/main   # main's package is exactly its release
```

CI runs `check` on every pull request: it reads which names appeared or
disappeared and which reference pictures changed, and fails unless the version
moved by exactly one step, at least as large as the change needs, with a
CHANGELOG section filled in. Merging a new version to `main` tags it
`v<version>` and publishes a release with `tikz-tensors-v<version>.zip`.

## Tests

```sh
tests/run.sh             # LuaLaTeX, pdfLaTeX, pdftoppm
tests/run.sh --update    # accept a deliberate change in appearance
```

Every file in `examples/` and `tests/cases/` must compile with both engines
without a warning, and every style and command must be drawn by one of them
(`tests/coverage.py`). The LuaLaTeX pages are then rendered and compared with
`tests/reference/*.png` (`tests/compare.py`, standard library only): a moved
leg, a changed colour or a lost label fails, and a `-diff.png` marks it in red.
In CI the rendered pages are the `rendered` artifact of the **CI** run.
`tests/cases/styles.tex` shows every style side by side — a new style is
added there.

## Licence

MIT.
