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
