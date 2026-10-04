# Commands

Every command a figure or a notation file may use, each with its keys. The
[overview](index.md) says how they combine into a figure; the
[styles](styles.md) are what they draw in.

### `\tnstack[<keys>]{<name>}{<sites>}{<layers>}`
A stack: `<sites>` slots across, the named `<layers>` down, placed on the
canvas after what is on the row.

| key | |
|---|---|
| `left=<label>`, `right=<label>` | an environment block at that end, drawn in `tn env` |
| `rises={<layer>=<factor>, ...}` | the gap above each named layer alone, at that factor of the stack's rise: `rises={g2=0.8, g3=0.8}` sets the layers of a circuit of gates closer |
| `scale=<factor>` | the whole stack at that factor of the notation: its distances, its tensors, its open indices |
| `pitch=<factor>`, `rise=<factor>` | ... or its distances alone, between sites and between layers |
| `size=<factor>` | ... its tensors, and the slots of absent ones |
| `stub=<factor>` | ... the least an open index of it shows |

A factor is a number, never a length, and multiplies the notation's tokens
for this stack only: `\tnstack[scale=0.7, rise=0.6]` draws a circuit of many
layers compact, and a stack after it is drawn at the notation's again. A
label keeps its size, which is the size of the equations beside it. A gap is
set where the stack is placed, `rises={g2=0.5}`, and not on `\tnlayer`,
because a layer's slots are named and placed before anything is put in them.

### `\tntree[<keys>]{<name>}{<sites>}{<layers>}`
A stack in the tree layout: at the tree's pitch and rise (`tree pitch`,
`tree rise`), each tensor its own size, centered over the sites it joins, and
an index between two that do not line up turning a corner. Its keys and its
layers are a stack's.

### `\tnlayer[<keys>]{<stack>}{<layer>}{<entry>, ...}`
The layer's slots, left to right: `<type>/<label>`, `<type>/<label>/<span>`,
`<type>/<label>/<span>/<down>`, `.` (empty), `-` (the layer's index runs
through), `|` (the site's index runs through), `+` (both run through,
crossing: a wire under the line of a gate on the sites either side), `dots`,
and `<n>*<entry>` for any of them repeated. A run of like entries is always
one `<n>*<entry>`.

| key | |
|---|---|
| `size=<factor>` | the layer's tensors at that factor of the stack's size |

### `\tngrid[<keys>]{<name>}{<columns>}{<rows>}{<type>/<label>}`
A square lattice of one tensor, turned by 45 degrees.

| key | |
|---|---|
| `bonds=<type>/<label>` | a tensor on every bond, turned with the lattice |
| `split` | every site drawn as the two halves of a singular value decomposition, as in the tensor renormalization group: triangles one above the other on the sites with i+j even, side by side on the others, their flat sides carrying the bonds of the lattice and their apexes joined; the type is the halves', four of them — `<top>, <bottom>, <left>, <right>`, the four tensors the splits leave — or one for all |
| `scale=<factor>`, `pitch=<factor>`, `size=<factor>`, `stub=<factor>` | as on a stack: the grid at factors of the notation's distances and sizes |

### `\tnconnect[<keys>]{<block>}`
Every index the block's layout implies.

| key | |
|---|---|
| `along=<edge type>` | the indices along the layers (on a grid, every bond) |
| `down=<edge type>` | the indices down the sites |
| `apart={<layer or port>, ...}` | layers with no index along them (a stack only), and ports whose bond is left out: `apart={g1, S-ket-2:right}` |

### `\tnopen[<keys>]{<direction>}{<tensor or block>, ...}`
Open indices toward `up`, `down`, `left` or `right`. On a grid, `down` (out
of the plane), or the lattice's own directions `nw`, `ne`, `se`, `sw` — the
indices toward that neighbour that no bond takes — or `around`, all four:
the edge of a piece of a larger lattice.

`rest` opens every index not yet drawn, each toward its own side: on a
tensor, all of its free ones; on a block, those of each tensor whose type
names its indices (`tn index`) — a type that does not has every index its
layout gives it, which is more than it means; on a port, that one index
(`\tnopen{rest}{W-a-2:u}`). An index left out by `apart=` is not opened. A
named index opened ends at the coordinate `<tensor>-<name>`.

| key | |
|---|---|
| `edge=<edge type>` | the edge type |
| `label=<text>` | a label at the end of each index, beyond it; `#1` is its number among the indices this command opens |
| `labels={<text>, ...}` | the labels one by one, in the same order |

### `\tnopenswap[<keys>]{<tensor>}`
The two indices down from a tensor across two sites, crossed. Its keys are
`\tnopen`'s: `edge=`, `label=`, `labels=`.

### `\tnjoin[<keys>]{<port>}{<port>}`
One index between two ports of one block; drawn from the first to the
second. A port is `<tensor>:<side>[:<n>]`, the `<n>`th index on that side
(the first unless said), or, of a tensor whose type names its indices,
`<tensor>:<name>` or `<tensor>:<n>`, its `<n>`th index in the type's order.

| key | |
|---|---|
| `edge=<edge type>` | the edge type |

### `\tneq[<keys>]`, `\tnapprox[<keys>]`
A relation sign after everything on the row; the next block goes after it.

| key | |
|---|---|
| `factor=<text>` | written after the sign, `\tneq[factor=$\lambda$]` |

### `\tnbreak`
The next block starts a new row, under everything drawn so far.

### `\tnframe[<keys>]{<tensor>, ...}`
A dashed box around the named tensors, said by what it frames: the tensors a
step contracts into one, or a part of a network set apart.

| key | |
|---|---|
| `label=<text>` | written above the frame's right corner |

### `\tntype{<name>}{<options>}`
A type of one's own: the style `<name>`, which is `<options>`, and which a
tensor drawn in it says it is — `\tnshow` and an error name it. It says what
a tensor is: its outline, its indices, named (`tn index`), which the layout
then holds a figure to, and which way they run (`tn flux`, or an index's own
`:in`, `:out`). In the preamble or a notation file:
`\tntype{site}{tn circle, tn index={l:left:in, r:right:out, s:down}}`.

### `\tnshow{<tensor>, ...}`
Writes what the package made of each tensor to the log: its block, the sites
and layers it covers, its type, how many indices it has and how many are
drawn, the sides it has them on, and each index — its name, if its type
names it, its side and place, and whether it is drawn, left out by
`apart=`, or free. Nothing is drawn; it is for finding out why a
figure looks as it does.

### `\tnput[<placement>]{<name>}{<text>}`, `\tnmid[<placement>]{<name>}{<name>}{<text>}`
A label at a named point, or midway between two. A label on an open index
goes in `\tnopen`'s `label=` instead.

### `\tnset{<key>=<value>, ...}`
The tokens, for a notation file (a figure may not use it).

| key | |
|---|---|
| `pitch=`, `rise=` | between sites, between layers of a stack |
| `tree pitch=`, `tree rise=` | the same, in a tree |
| `grid pitch=` | along a bond of a grid |
| `slot=` | the size of a tensor that is not there, where an open index ends |
| `stub=` | the least an open index shows beyond its tensor |
| `env width=` | the width of an environment block |
| `gap=` | either side of a relation sign; twice it between rows |
| `inset=` | how far a bond runs under the tensor it meets |
| `line width=` | the one stroke of outlines and indices |

### `\tnbond[<edge type>]{<path>}`
One edge drawn under the nodes, along a TikZ path written out. For extending
the package and for pictures that are not on a layout; a figure may not use
it.

