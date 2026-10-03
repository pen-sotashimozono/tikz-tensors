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
| `tree` | the tree layout: tree pitch, tensors at their own size, indices that turn corners |
| `close={<layer>, ...}` | layers that sit `closerise` under the layer above them instead of a rise, as the layers of a circuit of gates |

### `\tnlayer{<stack>}{<layer>}{<entry>, ...}`
The layer's slots, left to right: `<type>/<label>`, `<type>/<label>/<span>`,
`<type>/<label>/<span>/<down>`, `.` (empty), `-` (the layer's index runs
through), `|` (the site's index runs through), `dots`, and `<n>*<entry>` for
any of them repeated. A run of like entries is always one `<n>*<entry>`.

### `\tngrid[<keys>]{<name>}{<columns>}{<rows>}{<type>/<label>}`
A square lattice of one tensor, turned by 45 degrees.

| key | |
|---|---|
| `bonds=<type>/<label>` | a tensor on every bond, turned with the lattice |

### `\tnconnect[<keys>]{<block>}`
Every index the block's layout implies.

| key | |
|---|---|
| `along=<edge type>` | the indices along the layers (on a grid, every bond) |
| `down=<edge type>` | the indices down the sites |
| `apart={<layer>, ...}` | layers with no index along them (a stack only) |

### `\tnopen[<keys>]{<direction>}{<tensor or block>, ...}`
Open indices toward `up`, `down`, `left` or `right` (a grid: `down`).

| key | |
|---|---|
| `edge=<edge type>` | the edge type |
| `label=<text>` | a label at the end of each index, beyond it; `#1` is its number among the indices this command opens |
| `labels={<text>, ...}` | the labels one by one, in the same order |

### `\tnopenswap[<keys>]{<tensor>}`
The two indices down from a tensor across two sites, crossed. Its keys are
`\tnopen`'s: `edge=`, `label=`, `labels=`.

### `\tnjoin[<keys>]{<port>}{<port>}`
One index between two ports of one block, `<tensor>:<side>[:<n>]`; drawn from
the first to the second.

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

### `\tnput[<placement>]{<name>}{<text>}`, `\tnmid[<placement>]{<name>}{<name>}{<text>}`
A label at a named point, or midway between two. A label on an open index
goes in `\tnopen`'s `label=` instead.

### `\tnset{<key>=<value>, ...}`
The tokens, for a notation file (a figure may not use it).

| key | |
|---|---|
| `pitch=`, `rise=` | between sites, between layers of a stack |
| `closerise=` | between a layer and the one above where a stack names it `close` (the gap between two slots, halved) |
| `treepitch=`, `treerise=` | the same, in a tree |
| `gpitch=` | along a bond of a grid |
| `slot=` | the size of a tensor that is not there, where an open index ends |
| `stub=` | the least an open index shows beyond its tensor |
| `envw=` | the width of an environment block |
| `gap=` | either side of a relation sign; twice it between rows |
| `inset=` | how far a bond runs under the tensor it meets |
| `line width=` | the one stroke of outlines and indices |

### `\tnbond[<edge type>]{<path>}`
One edge drawn under the nodes, along a TikZ path written out. For extending
the package and for pictures that are not on a layout; a figure may not use
it.

