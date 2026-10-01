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

Also `env`, a boundary fixed point, which is what closes an infinite chain; and
`gate`, a box over several sites — a Trotter step, one term of an MPO — sized by
the caller, with `\tngatelegs` dropping its legs straight onto the sites, from
whichever side the gate is on, so that it can span any number of them.

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
