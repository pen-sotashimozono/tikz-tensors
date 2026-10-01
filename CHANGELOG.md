# Changelog

One section per version, newest first, headed by its tag. The version is the
`\ProvidesPackage` line of `tex/tikz-tensors.sty`; `scripts/version.py bump`
moves it and opens the section here, and the release on merge carries the
section as its notes.

## v0.3.0 — 2026-10-01

What a matrix-product state needs that the earlier notation could not say. Its
tensors are not all the same kind of object, and a picture that draws them alike
is a picture of a canonical form rather than one: `canl` and `canr` are the
triangles pointing the way the gauge runs, `centre` is the one tensor that is not
isometric, and `bond` carries the direction as an arrowhead on the leg.

Also `env` and `envc`, the boundary fixed points at the two ends, which are what
closes an infinite chain; `mpo`, an operator tensor sitting on the chain; and
`gate`, a bar over several sites — a Trotter step, one term of an MPO — sized by
the caller, with `\tngatelegs` dropping its legs straight onto the sites, from
whichever side the gate is on, so that it can span any number of them.

The theme moves to one eight-colour palette, and every colour in `[physics]`
changes with it, so a page that uses `ele`, `nuc`, `coef`, `exchange` or `exact`
is redrawn. A `[mps]` section joins it, one colour per kind of tensor, because a
chain is read by colour as much as by shape: the two canonical forms no longer
share one, the centre is a green diamond rather than another circle, and an
operator on the chain stays neutral grey so the state reads through it. The
tensors are filled rather than outlined — at the pale fills the single-tensor
styles use, a ten-site chain is ten outlines and the eye finds no site.

One consequence of the short style names, now that four of them also name a
colour (`coef`, `centre`, `mpo`, `gate`): TikZ resolves a bare option as a key
before it tries it as a colour, so `\fill[gate]` fills with the *style*. Write
`color=gate`, or `draw=`/`fill=`.

The centre has two places it can sit and the notation says both. `centre` is the
centre on a site, carrying a physical leg like its neighbours; `centrebond` is
the same diamond, smaller, for the centre on a bond — the Schmidt values, which
carry no physical leg. One SVD takes either form to the other, so they are one
shape in two slots rather than two shapes, and `examples/05-centre.tex` draws
the pair.

An outline and a leg are one stroke now. Every style draws with `tn line`
instead of carrying a width of its own, and `tn line width` (0.8pt) moves
outlines and legs together — on a picture, a scope or a single node — so a
figure can be set heavier without the nodes and the indices drifting apart.
`tn line` is public too, for a path the caller draws itself.

`scripts/version.py` guards keys defined with `/.code`, not only `/.style`, so a
public key like `tn line width` counts as a public name; `tests/coverage.py`
counts a key used with a value.

The page tokens go too. `[light]` and `[dark]` were a GitHub-style palette
chosen apart from the figures; every value in them is now one of the eight
mixed toward white or black, with the mix and the measured contrast written
beside it. The text tokens clear WCAG AA on their own background — `fg` 12.59:1,
`muted` 4.57:1, `accent` 4.52:1, `good` 4.61:1, `warn` 4.51:1, `bad` 6.90:1 in
light — which is why they are tints and shades rather than the pure colours: at
full strength the blue-grey is 2.72:1 and the green 2.14:1 on a near-white page.
`good` and `good-bg` join `warn` and `bad`, so the green is spent on a page as
well as in a figure. One limit is stated in the file rather than hidden: the
eight carry no red and no yellow, so `warn` and `bad` are the same warm family
and differ by weight, not hue, and a page must not separate them by colour
alone.

`examples/00-palette.tex` draws the map: a ramp per colour, the hex, and what
each one carries in figures and on a page. The ramps are mixed by xcolor from
the defined colour, so the page cannot drift from `theme/tokens.toml`.

`examples/02-swap.tex` exchanges two finite indices instead of two positions,
so its legs are straight. Wavy legs mean a continuous argument, and drawing a
swap of positions with straight ones would have contradicted the notation the
package opens with; the wavy form stays in `01-expansion`, and
`tests/cases/styles.tex` draws `\tnswap` both ways.

## v0.2.0 — 2026-09-29

Tensor-network diagrams only. `\tnnucleus`, `\tnelectron`, `\tncloud` and
`\tncoulomb` (Born–Oppenheimer style pictures) leave the package with their
examples: a project that needs them keeps them locally. What remains is the
notation (`fn`, `coef`, `op` and their wide/tall forms, `frame`, `cont`,
`disc`, `leg`), `\tnswap` and the shared theme.

## v0.1.0 — 2026-09-29

First version: one TikZ format for tensor-network diagrams — wavy legs for
continuous arguments, plain lines for finite indices, circles for functions,
squares for coefficient arrays — and a shared theme (`theme/tokens.toml`)
generating the TeX colours and a CSS file for notes and storyboards.
