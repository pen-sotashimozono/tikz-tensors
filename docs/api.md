# The interface

Everything a figure or a notation file may use, in one place. A name that is
not here is internal (`\tn@...`) and may change in any release.
`tests/coverage.py` holds this page and the code to each other: a public name
missing here, or a name here that the code does not define, fails the tests.
Until 1.0 a name may still be renamed or removed in a minor version, and the
CHANGELOG says so; from 1.0, only in a major one.

## Conventions

These are the rules every command keeps, so that one that is learned
predicts the rest.

- **Every optional argument is `key=value`.** No command takes a bare style
  or a bare text in brackets. (`\tnput` and `\tnmid` take TikZ's placement
  keys, `above`, `below=2pt`, and `\tnbond` TikZ's path options, which are
  keys too.)
- **The things a command draws are its mandatory arguments, in this order:**
  the block, then what in it (a layer, a direction), then the content.
- **Edge types are `edge=`**, and where a command draws two kinds of index,
  `along=` (along the layers) and `down=` (down the sites).
- **A figure places, then connects, then opens, then labels.** A block is
  placed (`\tnstack` and `\tnlayer`, or `\tngrid`), its implied indices drawn
  (`\tnconnect`), the rest opened or joined (`\tnopen`, `\tnjoin`), and only
  then are labels put on what is not an open index (`\tnput`, `\tnmid`).
- **Every index is drawn once.** Opening or joining one that is drawn
  already is an error; opening a whole block skips the ones that are taken.
- **No lengths and no coordinates in a figure.** Distances are tokens, set
  once in a notation with `\tnset`; positions are slots.

## Names a figure can refer to

| name | is |
|---|---|
| `<stack>-<layer>-<i>` | the tensor in slot i of a layer (one that spans is named by its first slot and top layer) |
| `<grid>-<i>-<j>` | the tensor at column i, row j of a grid |
| `<grid>-<i>-<j>-a`, `-b` | the tensor on the bond after it along a row, along a column (`bonds=`) |
| `<stack>-left`, `<stack>-right` | the environment blocks of a stack |
| `<stack>-<layer>-<i>-slot` | the center of a slot, tensor or not, including columns 0 and n+1 |
| `<stack>-<i>-<dir>` | the end of site i's index opened `up` or `down` on the whole stack |
| `<stack>-<layer>-<dir>` | the end of a layer's index opened `left` or `right` on the whole stack, or running from an environment block into an empty slot |
| `<tensor>-<dir>` | the end of a tensor's own index opened that way |
| `<tensor>-<dir>-<n>` | ... the n-th, when it has several that way |
| `<grid>-<i>-<j>-down` | the end of a grid tensor's index out of the plane |
| `<tensor>:<side>[:<n>]` | a port, for `\tnjoin` |

## Commands

### `\tnstack[<keys>]{<name>}{<sites>}{<layers>}`
A stack: `<sites>` slots across, the named `<layers>` down, placed on the
canvas after what is on the row.

| key | |
|---|---|
| `left=<label>`, `right=<label>` | an environment block at that end, drawn in `tn env` |
| `tree` | the tree layout: tree pitch, tensors at their own size, indices that turn corners |

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

## Styles

| style | |
|---|---|
| `tn node` | the bare tensor every type is built on |
| `tn box`, `tn circle`, `tn capsule`, `tn rounded`, `tn diamond` | outlines |
| `tn triangle right`, `tn triangle left`, `tn triangle up`, `tn triangle down` | triangles |
| `tn dot` | a copy tensor |
| `tn wide`, `tn tall`, `tn small`, `tn flat` | sizes |
| `tn fill` | solid fill, outlined in the one ink |
| `tn frame` | a dashed box |
| `tn gate`, `tn env` | the types a gate and an environment block are drawn in, for a notation to colour |
| `tn leg anchor`, `tn points`, `tn single` | a type's index properties, read by the layouts |
| `tn edge`, `tn wavy`, `tn arrow`, `tn double` | edge types |
| `tn arrows` | `tn arrows=false` turns every arrowhead off |
| `tn line`, `tn line width` | the one stroke, for a path of one's own |
| `tn label` | the text of a label |
