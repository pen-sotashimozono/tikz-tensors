# Changelog

One section per version, newest first, headed by its tag. The version is the
`\ProvidesPackage` line of `tex/tikz-tensors.sty`; `scripts/version.py bump`
moves it and opens the section here, and the release on merge carries the
section as its notes.

## v0.15.0 — 2026-10-03

A type says how many indices a tensor has, and the figure is held to it.

`tn rank=<n>` says a type's number of indices. When a picture ends, every
tensor whose type says a rank has that many of its indices drawn, joined or
opened, or the figure is an error naming the tensor, its type, and how many
are drawn -- an index left out by accident is caught where it is made. Not
said, a tensor has as many as the figure draws, as before.

`\tntype{<name>}{<options>}` declares a type: the style `<name>`, which a
tensor drawn in it says it is, in `\tnshow` and in an error. A rank smaller
than the sides its `tn legs` names is an error at once.

`\tnopen{rest}{<tensor or block>, ...}` opens every index not yet drawn, each
toward its own side: on a tensor all of its free ones, on a block those of
each tensor whose type says its sides. One left out by `apart=` is not.

`\tnshow` also writes a tensor's rank and how many of its indices are drawn.

The examples' notation declares its tensors with `\tntype`. No figure
changes. `tests/cases/types.tex` is the specimen: a chain whose ends have
rank 2 and bulk rank 3, a tree and a grid opened with `rest`.

## v0.14.0 — 2026-10-03

What a layout decides without being told, a figure can say and read back:
the first step toward types that carry their indices, as an ITensor does.

`tn legs={<side>, ...}` says the sides a type has indices on: up, down,
left, right (nw, ne, se, sw, down on a grid). Not said, a tensor has every
side its layout gives it, as before. Said, `\tnconnect` joins those sides
alone, `\tnopen` on a block opens them alone, and `\tnopen` or `\tnjoin`
naming another side of the tensor is an error.

`\tnconnect[apart=]` takes ports as well as layers: `apart={S-ket-2:right}`
leaves out that one bond.

A list of names takes ranges wherever a command takes tensors or ports:
`S-ket-{2..4}`, `P-{1..4}-2`, `S-b-{1..2}:right` (`\tnopen`, `\tnconnect`'s
`apart=`, `\tnframe`, `\tnshow`).

`\tnshow{<tensor>, ...}` writes what the package made of a tensor to the log:
its block, the sites and layers it covers, its type, the sides it has indices
on, and each index, drawn, left out or free.

No figure changes. `tests/cases/structure.tex` is the specimen of all four;
the styles page shows `tn legs`.

## v0.13.0 — 2026-10-03

The tensor renormalization group: a grid can be drawn split, and opened at
its edges.

`\tngrid[split]` draws every site as the two halves a singular value
decomposition leaves, as TRG splits a lattice: on the sites with i+j even the
halves are one above the other (`<grid>-i-j-top`, `-bottom`), on the others
side by side (`-left`, `-right`); each is one equilateral triangle turned
four ways, whose flat side carries its two bonds of the lattice and whose
apex meets the other half's, and `\tnconnect` joins them. The four halves are
four tensors, so the grid's type is four, `<top>, <bottom>, <left>, <right>`
(or one for all). The bonds of a split grid run corner to corner, and its
lattice is wider by 1.35, for the two tensors in each site.
`\tnopen` on a grid takes the lattice's own directions, `nw`, `ne`, `se`,
`sw`, and `around` for all four: the edge of a piece of a larger lattice, its
ends `<grid>-i-j-<direction>`, its labels beyond them on the diagonal.

`\tnframe[label=<text>]{<tensor>, ...}` draws a dashed box around the named
tensors: the tensors a step contracts into one.

New example, `24-trg`: a TRG step, the unit cell of two sites framed, the split of T in two ways and the
contraction of four halves into the T' of a lattice turned by 45 degrees. The
two that came after it are renumbered, `25-hotrg` and `26-toffoli`. In it
one colour is one tensor: T, T' a step paler, and the four halves S1 to S4,
each pair from one decomposition two steps of one hue (the examples'
notation names them `half1` to `half4`, and `coarse`).

On the documentation site, *Side by side*, beside an example's title, puts its
code beside its picture, the picture staying in view as the code
scrolls, so that pointing at a line lights up what it draws without the two
being a screen apart; the page remembers it, as it does the theme.

`tn size` scales a rounded outline's radius with it, so a capsule drawn
smaller stays a capsule; the gates of `26-toffoli`, drawn at 0.7, have
correspondingly smaller corners.

## v0.12.0 — 2026-10-03

Breaking: every scale of the palette runs in five steps, pale to dark, and
the steps that were there are renamed so that they keep their colours: on
blue, warm, green, yellow and purple, steps 1, 2, 3 are now 3, 4, 5 (`blue1`
is `blue3`, `warm3` is `warm5`), and steps 1 and 2 are new, the pale end of
each hue for fills that should recede. They carry the ladder of the given
steps on upward at each scale's own hue, so a scale greyish at its light step
stays greyish when pale (blue) and a clear one stays clear (green, warm). grey
cannot go paler than paper: its steps are paper `grey1`, a pale grey
`grey2`, the hairline `grey3` (was `grey2`), a middle grey `grey4` and ink
`grey5` (was `grey3`). Every figure draws as it did; a notation of one's own
that names a step moves its name the same way. `examples/00-palette.tex`
draws the five columns.

A block can be drawn at factors of the notation's distances and sizes, said
where it is placed: `\tnstack[scale=0.7, rise=0.6]`, and `pitch=`, `size=`,
`stub=`; `\tngrid` the same but `rise=`. A factor is a number, never a
length, so a figure may say it and `tests/lint.py` lets it through (a length
in the same place is still a finding); the factors are the block's own, and
the next block is drawn at the notation's again. Every command on the block
-- connect, open, join -- draws at its sizes. `\tnlayer[size=<factor>]`
draws one layer's tensors at a factor of the stack's, and the style
`tn size=<factor>` one tensor at a factor of its type's size; a label keeps
the size of the text.

A layer's slot can be `+`: the site's wire and the layer's line both run
through, crossing -- a gate on the sites either side of a wire. The style
`tn oplus` is a circled plus, the target of a controlled NOT, and the
examples' notation names `ctrl` and `targ`.

`\tnstack[rises={<layer>=<factor>, ...}]` sets the gap above one layer alone,
at a factor of the stack's rise.

On the documentation site, a figure lights up what a line of its code drew:
pointing at a line of an example's code marks, in red over the picture, the
tensors, labels and indices that line drew, and pointing at the picture
marks the line. It is read from a trace of each reference picture,
`tests/reference/<name>.json`, written while the tests compile (the new
`tex/core/tikz-tensors-trace.tex`, off in a document) and compared like the
picture. The walkthrough, the styles and the examples all have it.

New example, `25-toffoli`: the Toffoli gate of Shor's algorithm and its
decomposition into H, T, T† and six CNOTs, in thirteen steps drawn compact,
in a new section, quantum circuits. The styles page shows `tn oplus` and
`tn size`; the commands page the factors.

## v0.11.0 — 2026-10-03

`centre` is `center`, everywhere.

Breaking: the colour `centre` (and the theme token `--centre`) is `center`.
In the notation of the examples the styles `centre` and `centrebond` are
`center` and `centerbond`, and the example `09-centre` is `09-center`. The
comments, the docs and the reference use the American spelling as well. Every
picture is drawn as before; the palette's label for green1 reads `center`.

Stacks with layers at their own heights: `\tnstack[close={<layer>, ...}]`
sets those layers `closerise` under the layer above them instead of a rise --
the layers of a circuit of gates, drawn as one. `closerise` is a token
(`\tnset{closerise=...}`), by default the gap between two slots halved. A
figure says which layers; a notation says how close.

`17-trotter-sweep` is `17-trotter`, "Trotter steps": its first order is now
the even/odd splitting -- the gates on the even bonds as one layer, then those
on the odd bonds, two steps of it -- and the layers of gates in both of its
orders are close.

On the documentation site, every command of the package in a code block links
to its entry in the reference (`commands.html#tnopen`), and every style of it
to its own (`styles.html#tn-box`). The reference is three pages, from
`docs/reference/` (which replaces `docs/api.md`): an overview -- how a figure
is put together from a notation's declarations and the commands, the
conventions, the names -- then the commands and the styles. Each command and
each group of styles is a card of its own, with a button to its source; a
style's card shows its definition and a picture drawn with the commands
alone, and the last shows a notation's own styles in use. The overview builds
one figure a command at a time: each step's code, what it adds marked in red,
beside what it draws. A web address in an example's description is a link. The pictures,
`docs/reference/styles/` and `docs/reference/steps/`, are compiled and
compared as the examples are.

## v0.10.0 — 2026-10-02

Folders, and the abstract layout: stack, tree and grid as layouts of one kind.

`tex/` is in three folders: `core/` (core, canvas), `style/` (colors,
palette, nodes, edges, labels) and `layout/` (layout, stack, tree, grid). The
file names are unchanged and found by TeX's recursive search (`tex//`); a copy
of the package next to a figure takes every file, flattened.

`layout/tikz-tensors-layout.tex` is the abstract layout. A layout is a kind of
block with operations -- geometry, connect, open a block, open a tensor, join
two ports, the port of a tensor in a column -- and a kind inherits the ones it
does not define from its parent. `\tnconnect`, `\tnopen`, `\tnopenswap` and
`\tnjoin` are the same commands on every layout and hand their work to the
block's; a layout asked for what it cannot do says so. A new layout is one
file in `layout/`.
- The stack is a layout; the tree is a layout whose parent is the stack (its
  own pitch, tensors at their own size, indices meeting a tensor where its
  base takes them) -- no longer a flag the contraction rules test. Its bonds
  between layers are now drawn top to bottom like a stack's, which renders
  the same (`18-ttn`, `19-mera`: 0 pixels differ at 300 dpi; the references
  change).
- The grid is a layout: its tensors are recorded like a stack's, its bonds are
  drawn by `\tnconnect` and its physical indices by `\tnopen{down}`. Breaking:
  `\tngrid`'s `legs` option is gone; write `\tnconnect{P}` and
  `\tnopen{down}{P}` after `\tngrid{P}...` (`20-peps`, `21-simple-update`,
  which render exactly as before).

The interface, made one set of rules (`docs/api.md`, which a test now holds
to the code: a public name missing from it, or one it names that does not
exist, fails):
- Every optional argument is `key=value`. Breaking: `\tnopen[<style>]`,
  `\tnopenswap[<style>]` and `\tnjoin[<style>]` are `[edge=<style>]`;
  `\tneq[<factor>]` and `\tnapprox[<factor>]` are `[factor=<factor>]`.
- Labels on open indices are `\tnopen`'s (and `\tnopenswap`'s) `label=`, with
  `#1` the number of each index it opens, or `labels={...}` one by one; they
  sit beyond the end of the index. `\foreach` is no longer allowed in a
  figure, and every example that used it to label legs uses `label=`
  (rendering exactly as before). `15-cp` now puts the labels of its sideways
  indices beyond their ends, like every other, instead of above them.
- Breaking: the end of a layer's index from an environment block into an
  empty slot is `<stack>-<layer>-left` / `-right`, the name an index opened
  there has, instead of `<stack>-left-<layer>`.
- `apart=` on a grid is an error instead of being ignored.
- `scripts/version.py` tracks the interface exactly: the styles (`tn ...`) and
  each command's keys, instead of every pgfkeys path it found.

Ports are recorded once drawn. Joining or opening an index that is drawn
already is an error naming the tensor and the side; opening every index of a
block skips the ones that are taken, so an index joined by hand is not opened
as well. A name used again in a later picture is a new tensor.

## v0.9.0 — 2026-10-02

The package as modules; a tensor's indices as ports; `\tnjoin`, `<n>*`, `\tnset`.

`tikz-tensors.sty` is now a loader for nine modules in `tex/`, each a file,
each using only the ones above it: `core` (the stroke, the edge layer, the
tokens, `tn node`, `tn edge`, `\tnbond`), `colors`, `nodes` (node types and
the properties a layout reads off them), `edges` (edge types and routes),
`canvas` (rows, relations, `\tnbreak`), `stack`, `connect` (contraction),
`grid` and `labels`. Splitting the file changed no picture.

A tensor's indices are ports. A layout records where each tensor is; its type
says where an index leaves it; every index -- along a layer, down a site,
round the corner of a tree, open, or joined by hand -- starts at a port. An
index opened from the apex of a triangle now starts just inside its base, like
the triangle's other indices; it is hidden under the triangle (`23-hotrg`
renders identically at 300 dpi, but its reference changes).

New:
- `\tnjoin[<style>]{<tensor>:<side>[:<n>]}{<tensor>:<side>[:<n>]}` joins two
  ports the lattice does not: a periodic chain, a trace, a bond that skips
  its neighbours. Two ports facing each other on one line with nothing between
  are joined straight; any other index leaves each port by half a step into
  the gutter beside it (between two columns or two layers, where no tensor
  sits) and runs along gutters, so it never passes through or under a tensor.
  Example `24-periodic-mps`.
- `<n>*<entry>` in `\tnlayer`: an entry repeated, `4*canl/$A$`, `7*.`. The
  linter requires it for every run of like entries (rule `repeat`), so a layer
  has one spelling; every example is rewritten that way.
- `\tnset{<token>=<length>, ...}` sets the package's spacing (pitch, rise,
  slot, stub, gap, ...) and line width, for a notation file; a figure cannot
  (the linter forbids it there, and `\tnbond`).

`0*<entry>` is an error (a run is one entry or more).

Fixed: two neighbouring `-` slots are now joined (they were left apart).

Removed (before 1.0, so a minor step): `\tnchain`, `\tnrow`, `\tnlegs`,
`\tngate`, which placed tensors by coordinates and which no example used since
v0.6.0; the stack does all of it. `\tnswap` is internal now; `\tnopenswap`
draws the crossing.

## v0.8.0 — 2026-10-02

Two-dimensional networks: PEPS, simple update, CTMRG, HOTRG.

Roadmap phase 4. `\tngrid[legs, bonds=<style>/<label>]{<name>}{<columns>}{<rows>}{<style>/<label>}`
draws one tensor repeated over a lattice, each joined to its neighbours,
turned by 45 degrees so the lattice reads as a plane seen from above and the
physical indices (`legs`) go straight down without crossing a bond. `bonds=`
puts a tensor on every bond, half way along. It is placed as a stack is, so it
takes part in rows and equations.

New examples: `20-peps` (a four-by-four PEPS), `21-simple-update` (Gamma on
the sites, lambda on the bonds), `22-ctmrg` (the corner transfer matrix
environment of one site, on an ordinary stack) and `23-hotrg` (two tensors
coarse-grained into one, the fusing isometries a triangle up and a triangle
down, again on a stack). In the notation: `corner` and `side`, the
environment of a two-dimensional network in the environment's colour, and
`isodown`, an isometry pointing down.

No tensor of the notation is a square any more. `coef` is a circle in the
array colour (`coef` = `blue1`): a `tn capsule`, whose corners are now half
its height, so it is a circle at one site's size and stretches to a stadium
across several; `op` is
a plain rounded box; a CTM side is a circle. Rounded boxes stay what they were
(an MPO tensor, a gate, a corner). A square says nothing a circle does not,
and on a lattice turned by 45 degrees it reads as a diamond. `03-mps` loses
its second row, which compared the two.

On a grid, a tensor on a bond is turned with the lattice, so that the bond
meets it as it would on a chain — at a vertex of the diamond, not the middle
of a side — with its label upright.

Not yet: TRG, which splits each tensor along a diagonal of the lattice and
needs an index that is neither along a layer nor down a site.

## v0.7.0 — 2026-10-02

Trees, MERA and the decompositions, on the same grid.

Roadmap phase 3. New examples: `17-svd-qr` (T = U S V† and T = Q R on one
tensor of a chain), `18-ttn` (a tree on sixteen sites: four tiers of isometries, sixteen to one,
and the centre on top) and `19-mera` (a binary MERA on sixteen sites: four
tiers of coarse-graining and the top tensor).

- **Triangles pointing up and down.** `tn triangle up` and `tn triangle down`
  stretch to the sites they span, so an isometry of a tree or a MERA is as
  wide as what it joins. `tn single` says on which side a shape has one index
  however wide it is; `\tnopen` on that side opens one, from the middle.
- **One rule for every vertical index.** Two tensors over the same sites meet
  on each of them, as before. Otherwise they meet once, in the middle of the
  sites they share. That one rule places a site under a gate, a branch under
  its node, and an isometry of a MERA under a disentangler that overlaps it by
  half; no example says where any of them goes.
- **Into a triangle from the side.** An index meeting a triangle away from its
  apex ends just inside the base, not at the middle, which off the apex is
  outside it.
- **`\tnstack[tree]`** draws a stack as a tree is usually drawn: a tensor
  across several sites keeps its own size, centred over them, the sites are
  half the pitch apart, and an index between two tensors that do not line up
  turns a corner — up from the lower one, across at half height, up into the
  base of the upper one — instead of stretching either. `18-ttn` and
  `19-mera` are drawn this way; a chain is not, because there the stretched
  gate laid on its indices is the point.
- **Rows keep the slot above them**, as stacks keep the slots beyond their
  ends, so an index opened upward on a second row clears the first. Every
  picture with two rows is a little taller.

`tn flat` is a shape resized flat (10.5 mm by 6 mm), as a tree's tensors are
drawn.

In the notation: `iso`, a flat triangle pointing up, toward the root, in the
left-canonical colour — off a chain there is no left and right, only toward
the centre; and `disentangler`, a gate drawn flat.

Outside the package (no version step of its own, carried here):

- **The pictures are compared as SVG.** `tests/reference/` holds the
  `pdftocairo -svg` of every page instead of a 180 dpi PNG, and
  `tests/compare.py` matches them as drawings — every path and every glyph,
  glyphs by their shape rather than their id, numbers within a quarter of a
  point. Rasterising had to be compared with a pixel tolerance a moved leg
  could hide in; the SVG is the drawing itself, a quarter the size, readable
  in a diff and shown as it is by GitHub. A page that fails gets a
  `-diff.txt` of what is only on one side.
- **CI is split by role**, each job on its own runner: `rules` (coverage and
  the figure rules, no TeX), `compile` (one runner per engine), and `test`,
  which waits for those, says whether they passed, and compares the pictures
  and posts the preview from the LuaLaTeX job's PDFs — so the check the
  ruleset on `main` requires keeps its name and its meaning. `tests/run.sh` takes the same steps as arguments
  (`compile <engine>`, `rules`, `compare`) and runs them all with none.
- `examples/out/` is no longer committed: the README shows the reference
  SVGs, which are the same pictures.

## v0.6.0 — 2026-10-02

Every example on the grid, and what MPO times MPS needs.

**Every example is on the grid now**, and the lint ratchet is empty:
`tests/lint-legacy.txt` lists nothing, and no example has a length, a
coordinate or a raw TikZ command in it. The ones written by hand are rewritten
on stacks and named for what they draw:

| was | is |
|---|---|
| `01`–`05` | the same names, rewritten |
| `07-fixed-point` (two conventions side by side) and `12-fixed-point` | `07-fixed-point`: both fixed-point equations, the physical index from the flat side |
| `08-tebd` | `08-trotter-sweep` |
| `13-low-rank` | `12-low-rank` |

New, for what the product of an MPO and an MPS needs (roadmap phase 2):
`13-mpo-mps` (the naive product, with fused bonds), `14-zip-up` (the sweep
caught halfway, its zipper two layers tall), `15-cp` (a CP decomposition, the
shared index a copy tensor) and `16-sampling` (an amplitude, every index closed
by a basis vector).

What the grid learned to do for them:

- **Rows.** `\tnbreak` starts a row under everything drawn. A stack after a
  stack, with no relation between them, stands beside it.
- **More slot kinds.** `|` is a slot the site's index runs through, so the
  sites a gate does not touch run on past it and every index ends at one
  depth; `dots` is the dots of a chain that goes on.
- **Tensors across layers.** `<style>/<label>/<span>/<down>` is as tall as
  the layers it covers and has an index into each — the zipper of zip-up.
- **Opening a whole stack.** `\tnopen{down}{S}` opens every site's index from
  its lowest tensor (`S-<i>-down`), and left/right every layer's.
  `\tnopenswap` opens two crossed, which is 02.
- **Arrows from the shapes.** A bond is drawn border to border, and one that
  carries a direction takes it from the triangles it joins: `tn points`, which
  the triangles set. Every arrow of a canonical form points at the centre
  without being written, and an open bond at either end points in.
- **Connect options.** `\tnconnect` takes `along=` and `down=` separately, so
  bonds carry arrows and physical indices do not, and `apart=` for layers whose
  tensors have no index between them.
- **New shapes.** `tn dot`, a copy tensor; `tn double`, two indices fused into
  one. The notation calls them `delta` and `fused`, and a basis vector `basis`
  (a small circle).

Geometry changes, so every stack figure is redrawn:

- The pitch across is 18 mm, so a triangle set across in its slot leaves room
  for a bond and an arrowhead before the next tensor. Down, layers stay 15 mm
  apart (`rise`).
- A stack without an environment keeps its end slots as far as their borders,
  so an index opened at either end never runs into the relation sign beside it.
- A label counts as drawn when the next sign is placed.

One trap is documented rather than removed: a style with a comma in it, or a
label with a slash, goes in braces (`{coef, circle}/$A$`,
`gate/{$U(\delta t/2)$}/2`), and the dots are `dots`, not `...`, which
`\foreach` reads as a range.

## v0.5.0 — 2026-10-02

Stacks: a figure of an algorithm drawn on a grid the package owns, so that two
authors drawing the same algorithm write the same file (`docs/roadmap.md`).

A stack is n sites across and a list of named layers down — `ket`, `op`, `bra`,
or as many as a picture has — at one pitch both ways, and a tensor is put in a
slot rather than at a point. `\tnstack` places it, centred on y = 0 and to the
right of what is already drawn, with an environment at either end if asked;
`\tnlayer` fills a layer, one entry per slot (`<style>/<label>`, a tensor across
several slots as `<style>/<label>/<span>`, `.` for an empty slot and `-` for one
the layer's index runs through); `\tnconnect` draws every index the grid
implies; `\tnopen` adds the open ones; `\tneq` writes an equals sign and moves
on. An open index ends at the border an absent tensor of the standard size
would have, so the gap in a picture of H_eff is the shape of the state that is
missing from it, and none of those ends is written down.

**The package's styles are shapes, not meanings.** What a circle on a wavy
leg stands for, or a triangle, or a diamond, is a notation, and a notation is
its user's: the package now draws and places, and says nothing about meaning.

| was | is |
|---|---|
| `coef`, `op` | `tn box` |
| `fn` | `tn circle` |
| `fnwide`, `fntall`, and `coefwide` … `opwide` | `tn capsule` or `tn box` with `tn wide` / `tn tall` |
| `mpo` | `tn rounded` |
| `gate` (the style \tngate draws with) | `tn gate` |
| `canl`, `canr` | `tn triangle right`, `tn triangle left` |
| `centre`, `centrebond` | `tn diamond`, `tn diamond, tn small` |
| `frame` | `tn frame` |
| `disc`, `cont`, `gauge` | `tn edge`, `tn wavy`, `tn arrow` |
| `leg` | `tn label` |
| `tn round`, `tn swap cont`, `tn swap disc` | gone (`circle`; \tnswap draws its crossing in its own style, undecorated) |

Every old name is still available, as a style of
`examples/conventions/notation.tex` — the notation this repository's examples
are drawn in, and an example of the file a project keeps for its own. Each
example `\input`s it after the package (`tests/run.sh` and
`scripts/build-examples.sh` put `examples/conventions/` on `TEXINPUTS`), and
every example renders exactly as before. A document that used the old names
needs the same one line, or its own copy of that file. The default style of
`\tnbond`, `\tnlegs`, `\tnconnect` and `\tnopen` is `tn edge`, and of
`\tnswap` `tn edge` too (was `cont`).

The shapes carry paper fill, so an index drawn to a tensor's centre is covered
by it; `tn node` stays unfilled. Colours are unchanged, and the theme still
names them by meaning (`ele`, `canl`, …): that is the theme's vocabulary, used
by a notation to colour its styles.

The block at the ends of a stack (`tn env`) is new, and so is an environment
in the notation (`env` colour). It is not the `env` removed in v0.3.0, which put an object at the
end of a finite chain, where the outer bonds carry nothing. This one is the rest
of the network, contracted — the L and R of DMRG and TDVP, the fixed points of a
uniform state — and it spans every layer of its stack with one index in each.

Colours, within the ramp as it is: in the notation an environment is light
purple (`env` = `purple1`, at the 25% fill the gate used to have), and a gate is
now light yellow (`gate` = `yellow1`). Purple for the environment, which is large and
should recede; yellow for the gate, which is the thing being applied. Every page
with a gate on it is redrawn.

`examples/06-dmrg.tex` is rewritten on stacks as `06-heff-two-site`, and
`examples/09-expectation.tex` in place; neither has a length or a coordinate in
it, and both come off the lint ratchet. New: `10-heff-single-site` and
`11-heff-bond`, the single-site and bond effective Hamiltonians, and
`12-fixed-point`, the left fixed point of a uniform MPS as an equation of two
stacks. `13-low-rank` is a five-site tensor and its MPS approximation,
side by side: one entry spanning five slots is exactly as wide as five sites, so
the two share their width, their columns and the depth of every index without
the file saying so. `\tnapprox` is `\tneq` with an approximately-equals sign.

In a stack a triangle's physical index leaves from the corner of its flat side,
not its centre: the index continues that side's own line, which is how a
canonical form is read. The triangle is set across in its slot so that the
corner is on the site's line, and the grid stays straight. A shape says where
its index leaves with `tn leg anchor` (the triangles set `corner 3` and
`corner 2`; everything else is its centre). The pitch is 15 mm, so that a
triangle moved across still clears its neighbour, and an open index shows at
least 4 mm beyond its own tensor.

`tests/cases/inline.tex` has the expansion twice: drawn downward, and along the
line as one stack, which `baseline=-0.5ex` sets on the math axis — the one to
copy for running text. Examples are named for the object they draw, not the algorithm that
uses it: one H_eff serves DMRG, TDVP and VUMPS alike. `07-fixed-point` stays as it is: it compares two places the physical
index can leave a triangle, and a stack takes it from the centre.

## v0.4.0 — 2026-10-02

`\tnrow` places tensors left to right, each a given gap clear of the one before
it — measured between their borders, not their centres, so the spacing is right
whatever shapes and sizes are in the row and stays right when one of them
changes. `\tnchain` spreads a row evenly along a line, which is what a chain of
like tensors wants; this is for a row of unlike ones, where the distance that
matters is the gap and working the centres out by hand is both tedious and the
first thing to go stale. Site i becomes `<prefix>i` and `<prefix>i-leg`, as in
`\tnchain`.

The superblock in `examples/06-dmrg.tex` is built on it: a row of two shapes of
different widths and heights, and not one position in it written out. Its free
indices end where the absent two-site tensor's own legs would be — the bond
indices at that tensor's centre height, the physical ones half its height
shorter, at its near edge — because a gap is only a gap if what is missing would
fit in it. They are deliberately not all at one depth: a tensor's bond legs and
its physical legs do not leave it at one height either.

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

A physical index is the triangle's own outermost line carried on down. `\tnlegs`
takes `l` and `r` at the bottom corner of a canl or a canr triangle's flat side,
and since that side is vertical the index continues it as one straight stroke
rather than sprouting from anywhere. The two gauges mirror each other in the
index as well as in the shape, and `c` is still there for a box, a circle or a
diamond, which have no such line to continue.

A bond reaches the tensor it runs to. `tn node` sets `outer sep=0pt`: TikZ keeps
a path half a line width clear of a node's border so that it meets the outside
of the stroke rather than overlapping it, but `minimum size` already counts the
stroke, so the border *is* the outside of it and the clearance is added twice.
Measured at 700 dpi on two canl triangles, a one-pixel gap between the tensor
and its bond; after, one continuous run of ink. Same cause as the index not
lying on the edge — the shape's nominal boundary is not the line that is drawn.

An anchor lands on the line that is drawn, which is what `outer sep=0pt` buys
besides the bond join: TikZ's default outer sep is half a line width and it is
added to every anchor as well as to the border, so a corner anchor sat that far
outside the stroke and an index placed on it ran beside the tensor's own edge
rather than along it. Measured on a canl triangle: `corner 3` at −7.86884pt with
the default and −7.46884pt without, exactly half a width apart. One cause, two
symptoms, one fix. The test is the obvious one — extend the index upward past
the top of the tensor and it covers the edge with no black showing beside it,
at the examples' own scaling as well as at none.

The join is closed by starting the index inside the tensor, which covers the
overlap because nodes are drawn over the edge layer. Begun exactly on the
corner, the index's stroke ends half a line width short of where the outline's
stroke ends and the join reads as a gap. The overlap is upward only — moving the
point toward the centre instead would close the gap but take the index off the
flat side's line, which is the whole point of taking it from there.

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
