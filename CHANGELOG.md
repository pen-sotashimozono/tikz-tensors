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

The uneven outlines a box can show in the rendered test PNGs are recorded in
`tests/run.sh` rather than fixed, because the fix was measured and was worse.
TikZ is not the source: the PDF carries one line width per stroked path, so
there is no top-against-bottom to get wrong. poppler's Splash backend snaps a
thin axis-aligned stroke to whole pixels without anti-aliasing, so the two
edges of a box round independently by where each lands — 18 of the 157 columns
crossing a box on the specimen sheet have their strokes more than half a pixel
apart in ink, the worst 0.80 px. It is a phase effect, not a resolution one, so
no dpi avoids it. `pdftocairo` cuts it to 3 of 157, but its anti-aliasing
differs between poppler versions and the references then failed against the
runner's render on six of eight pages; this test exists to be reproducible, and
snapping is. Nothing a document shows is affected either way — `build.sh` gives
the documents SVG and PDF, and these PNGs exist only to be compared.

`tests/cases/styles.tex` is a specimen sheet rather than a picture. Each public
style and command stands on its own with the name it is there to show written
under it, so what the file is for can be read off it. The one group kept
together is the chain, because a triangle alone says nothing — "isometric from
this side" needs the other side and the centre to be read against. What was
there before had `tn arrows=false`, a one-site gate and `centrebond` welded into
a single chain with a gate `V` on it, which looked like a diagram making a claim
and was only three unrelated coverage needs sharing a picture.

`tests/coverage.py` now says what its match cannot prove: it is textual, so
where a style and a colour share a name (`coef`, `centre`, `mpo`, `gate`) the
colour's swatch satisfies the style.

A tensor is drawn over the index it carries, and that is now the package's job
rather than the caller's. Every edge `\tnbond`, `\tnlegs`, `\tngatelegs` and
`\tnswap` draws goes on a layer beneath the nodes, so the rule holds whatever
order a file is written in — before, a leg drawn after a node was drawn across
it, which is what happened to the operator row in the style sheet. (`\pgfsetlayers`
is global: `main` stays on top, `tnedges` is added under it.)

`\tnbond` takes the whole path, so an index can end on a node, on a coordinate,
or on nothing at all: `\tnbond{(A1) -- (A2)}`, `\tnbond{(A3) -- ++(0.55,0)}`.
An open index needs no far end, and the finite chains in the examples use that
for their outer indices — drawn inward, so the arrowhead runs toward the centre
like every other bond.

The gate is pale: `gate!25` with ink, outlined in `gate!85!black`. The state
tensors keep the fills they had. A gate is applied *to* the state and should
read behind it, and at equal weight the two competed.

`\tnchain` takes a line and puts the tensors on it — evenly between its two
ends, or stepped along it by a given pitch — and says, once, where each one's
index leaves it: site i becomes the node `<prefix>i` and the coordinate
`<prefix>i-leg`, and everything that connects to that site — its own leg, a
gate's leg, an operator row beneath it — connects to that coordinate.
`\tnlegs`, `\tngate` and `\tngatelegs` take points now, not a node and a side.

The point was that a connection was being re-derived at every use. Counted
across the two examples and the specimen sheet before: 27 spellings of a corner
anchor and 40 literal site coordinates, with one site's connection point written
out four separate times. After: no corner anchors at all, and the only literal
coordinates left are where a specimen sits on the sheet.

`\tnlegs` and `\tngate` take a drop rather than a height, so nothing in a
picture is a y to be worked out; `\tnput` and `\tnmid` place a label by what it
labels — above this tensor, below that index's end, midway along this bond —
rather than at a coordinate. `04-canonical` is down to the two coordinates of
its one line and `05-centre` to those plus two offsets from them; before this
pass there were 40 literal coordinates across the two examples and the specimen
sheet.

`\tngatelegs` is gone. A gate needs no legs: the indices run past it and a node
covers an edge, so a gate placed on them interrupts them, which is what applying
one looks like and is one fewer thing to keep in step.

One picture moves because of it. `\tngate` measures the points it is given, so
it now spans the indices it acts on rather than the sites' centres, and the gate
in `04-canonical` is narrower and sits over its two legs — 3.9% of drawn pixels.
`05-centre` is byte-identical, which is the check that nothing else moved.

The chains are drawn at a wider pitch. A bond meets a triangle at its apex,
which is a point, and at the old pitch the gap from that tip to the next tensor
was 3.5mm with a 1.7mm arrowhead wedged into it. At 1.3 times the pitch the gap
is 7.6mm and the arrowhead sits in open bond. Neither the shape nor the notation
changes; the line `\tnchain` is given is simply longer, which is the one knob
that reaches this.

The examples take their physical indices from the centre again. `\tnlegs` still
offers `c`, `l` and `r`, but a triangle's flat side is vertical, so a leg from
its bottom corner continues that side as one straight line and the tensor reads
as a flag on a pole.

A site's connection point sits a little inside the corner rather than on it. A
corner anchor is on the outline's path and the outline is stroked about that
path, so a leg starting exactly there pokes half a line width past the edge: at
700 dpi, three columns of leg with nothing above them, which reads as a leg
detached from its tensor. `\tnchain` moves the point an eighth of the way to the
centre — about half a millimetre at this size, so it still leaves from the
corner as far as the eye is concerned — and the tensor, drawn over the edge
layer, covers the overlap.

Every outline in a diagram is one ink, not only the ones no preset had
overridden. `tn fill` keeps the default outline and sets only the fill, so a
tensor's colour is its fill and the stroke is the same as the index it carries —
which is the rule holding in a picture of a chain rather than only in the
abstract.

The reference images are rendered at 180 dpi. Splash snaps a thin axis-aligned
stroke to whole pixels, so where a stroke is not a whole number of them two
strokes of the same width round differently: at 150 dpi the five legs of
`05-centre` came out 0.8, 0.8, 1.6, 1.6, 1.6 in ink — half of them twice the
weight of the others, plainly visible. 0.8pt is whole at every multiple of 90,
and measured there the legs are uniform (180, 270, 360) and ragged between (150,
200, 300). This fixes the widths, not the phase effect itself, so the one demo
of `tn line width` is 1.6pt (4 px at 180) rather than 1.8pt (4.5 px).

A tensor's outline and an index are drawn in one ink by default. The theme's
`[figure] stroke` names it, `tn node` and `tn edge` both take it, and a preset
that means something by its colour says so for itself. It is `grey3`, which is
`black!80` to the pixel — so the edges do not move, only the outlines that were
in the page's text ink: 1187 pixels of the specimen sheet change from `#00344d`
to `#333333`, and the 553 that stay are the labels. `grey3` was the last step
that nothing named, so the count on the palette chart goes to 14 of 18.

A network is nodes and edges, and those come first: `tn node` is a tensor,
`tn edge` an index, `tn fill` the solid-colour convention. A diagram can be
drawn out of those three with no notion of what is a state and what is an
operator — which is the normal case, since most networks have no such
distinction — and every name below them is a preset built on them, for the cases
that do. `tn node` draws an ink outline rather than leaving `draw` unset,
because a node with no `draw` is not drawn at all.

One consequence, visible in `01-expansion`, `02-swap` and `03-mps`: `tn node`
carries `text=ttfg`, so a tensor's label is the theme's ink everywhere rather
than plain black in some presets and ink in others.

`bond` is gone and `gauge` takes its place. A bond does not have a direction —
it is an index, and an index is just an index — so the plain `disc` is the bond,
`\tnbond`'s default is `disc`, and `gauge` is for a picture where the direction
is known and is part of what is being said. `tn arrows` still turns those
arrowheads off.

A physical leg can leave a tensor two ways and `\tnlegs` says which: `{c}` from
the centre, clipped at the node's border — the only thing a box, a circle or a
diamond can do — or `{l}` and `{r}` from the bottom corner of a canl or a canr
triangle's flat side, so the two gauges mirror each other in the legs as well as
in the shape. Those are `corner 3` and `corner 2`: the two triangles are one
shape at a 180° turn, so no single index names both, and `south west` sits on
the edge above the vertex rather than on it. Every leg in one call ends at the
same depth.

`\tngate` sizes and places a gate from the sites it acts on, so no width is
written by hand and a gate cannot drift off its sites when the chain is
respaced. One site gives a small box, several a bar. It measures centres, not
legs, so the default padding (6mm) clears a leg taken from a triangle's corner,
which at the default 10.5mm sits 4.55mm off centre.

The gate takes `purple1` with ink text — a light step in the chain's own
register, and a hue nothing else uses, since a gate is neither a state tensor
nor an operator on the chain. It was `blue2` with white text: a saturated fill
in a picture of pale ones, and 2.98:1 for ink or 4.41:1 for white, against
4.75:1 for ink on `purple1`.

`tn arrows` turns the arrowhead on a `bond` off, for a picture that is not about
the gauge; `scripts/version.py` guards a key defined with `/.is if` as it
already guards `/.style` and `/.code`.

`env` and `envc` are gone, and with them the `edge` and `edgec` colours that
nothing else named. The examples are finite chains: the outer bonds are
one-dimensional and carry nothing, and a picture of a finite state should not
put an object there.

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

The codes are two scales, not eight colours, and `[ramp]` now says so: blue in
three steps light to dark, warm in three, plus a green and a grey. Every other
value names a step — `blue2`, `warm3 +25% white` — and no hex is written twice,
so a code is written once and a meaning is an assignment onto it. A pair that
should read as a pair takes the same step on the two scales: `canl`/`canr` at
step 1, `edge`/`edgec` at step 3. `scripts/theme.py` resolves a step and its
mix; restructuring moved no value, which the generated files show as eight
added lines and nothing changed.

Grey becomes a scale too: `grey1` paper white, `grey2` the hairline grey that
was simply `grey`, `grey3` ink `#333333`. That removes the last literal from the
table — `card` was `#ffffff` written out, the one value off a scale — and
`scripts/theme.py` now refuses a literal outright: every value must name a step,
which is what makes "a code is written once" an invariant rather than a habit.
`grey3` is defined and unused.

Three more scales — green, yellow, purple — built on the ladder the two given
ones measure out in CIELCh: step 1 near L\* 62–74 at about 40% of the chroma
the gamut allows there, steps 2 and 3 near L\* 50–60 and 35–42 at about 85%,
capped in absolute chroma as well, since purple's gamut is three times blue's at
the same lightness and a fraction of it alone comes out neon. `green` is renamed
`green1` and keeps its code; `green2` and `green3` are built under it. Yellow
turns gold and then ochre as it darkens, which is what a yellow does — one light
enough to stay yellow is too light to put text in.

`warn` moves onto the yellow scale (`yellow3`, 5.72:1 on the light page, and
`yellow2 +15% white` at 7.75:1 on the dark one). It and `bad` were two steps of
the one warm scale, told apart only by weight; they are now about 30 degrees
apart in hue. The caveat in `theme/tokens.toml` shrinks to what is still true:
there is no red, so `bad` is the darkest warm rather than a red.

`examples/00-palette.tex` is a row per scale — the scale mixed step to step so
its direction is visible, then the three steps with their names, hex and roles.
No colour appears on that chart that the theme does not define. The steps are
three discrete blocks, not a bar running one into the next: a gradient looks
like a continuous scale, and between two steps there is nothing. What does exist
beside a step is a tint or a shade of it — the page tokens — and those are drawn
as chips in the colour they actually are, each labelled with the token and the
mix that makes it.

Nothing on that chart is written on it. `scripts/theme.py` generates
`tex/tikz-tensors-palette.tex` — the scales, the steps, the hex, the roles and
the count — out of `theme/tokens.toml`, and the example is the layout and
nothing else, so the chart can only say what the table assigns.
`scripts/theme.py --check` covers it, which the `theme` job already runs.

The first hand-written version of those captions was incomplete in five places:
`blue1` also carries `soft` and the dark `fg`, `blue3` also carries the dark
`card`, `soft` and `line`, `warm3` and `green1` also carry a `-bg`. A step that
nothing names is blank, and the generated count says how many: 16 steps defined,
11 named by something, `green2`, `yellow1` and the three purples unused. Every
step does exist as a colour — `\definecolor` in the TeX and a custom property in
the CSS — so an unused one is callable, not a label with nothing behind it.

`good` takes pure steps instead of a mix: `green3` on the light page (6.71:1,
where the mix it replaces was 4.61:1) and `green1` on the dark one.

`tn round` draws a node as a circle. Square against circle is this package's own
distinction and only earns its keep where both kinds are on the page; a plain
tensor network has no functions in it, and much of the literature draws every
tensor there as a circle. `examples/03-mps.tex` draws one chain both ways —
same style, same colour, same meaning. Shape still carries meaning in a
canonical form, where a triangle says isometric and a diamond says centre, and
`tn round` does not touch that.

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
