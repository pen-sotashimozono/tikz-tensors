# Styles

A type is a TikZ style. Every tensor in a `\tnlayer` entry is drawn in one,
and every index in one given as `edge=`, `along=` or `down=`. The package's
styles are shapes and lines, each built on TikZ and on the ones before it —
`tn box` is `tn node` as a rectangle, at a size, filled with paper — so what
a style draws is what its definition says. Each one below shows its
definition and a picture drawn with the package's commands and nothing else.

A notation builds styles of its own on these, named for what they mean, and a
figure uses them wherever it would use the package's: the last entry is one,
and `examples/conventions/notation.tex` is the one the examples are drawn in.

## Tensors

### `tn node`
[picture](styles/style-node.tex)

### `tn box`, `tn circle`, `tn capsule`, `tn rounded`, `tn diamond`
[picture](styles/style-outlines.tex)

### `tn triangle right`, `tn triangle left`, `tn triangle up`, `tn triangle down`
[picture](styles/style-triangles.tex)

### `tn dot`, `tn oplus`
[picture](styles/style-dot.tex)

### `tn wide`, `tn tall`, `tn small`, `tn flat`, `tn size`
[picture](styles/style-sizes.tex)

### `tn fill`
[picture](styles/style-fill.tex)

### `tn gate`, `tn env`
[picture](styles/style-gate-env.tex)

### `tn site anchor`, `tn flux`, `tn single`, `tn index`
[picture](styles/style-index.tex)

## Indices

### `tn edge`, `tn wavy`, `tn arrow`, `tn double`
[picture](styles/style-edges.tex)

### `tn arrowheads`
[picture](styles/style-arrows.tex)

### `tn label`
[picture](styles/style-label.tex)

## Paths of one's own

### `tn line`, `tn line width`
[picture](styles/style-line.tex)

### `tn frame`
[picture](styles/style-frame.tex)

## A notation of one's own

### Your own styles
[picture](styles/style-own.tex)
