# The interface

Everything a figure or a notation file may use is on these pages: this one,
how a figure is put together and the rules every command keeps; the
[commands](commands.md), each with its keys; and the [styles](styles.md),
each with what it is built on and a picture. A name that is not on them is
internal (`\tn@...`) and may change in any release. `tests/coverage.py` holds
the pages and the code to each other: a public name missing here, or a name
here that the code does not define, fails the tests. Until 1.0 a name may
still be renamed or removed in a minor version, and the CHANGELOG says so; from
1.0, only in a major one.

## How a figure is made

A figure is made of two kinds of statement, kept in two places.

- **Declarations, in a notation file, once for every figure.** What a kind of
  tensor or index looks like: a type named for what it means, built on the
  package's styles (`\tntype{canl}{tn triangle right, tn fill=canl}`), which
  may also name its indices (`tn index`); an edge type, a TikZ style; and the
  distances, with `\tnset`. The examples' notation is
  `examples/conventions/notation.tex`.
- **The network, in the figure.** Which tensors there are, of which kind, and
  how they are contracted, in this order:

| step | commands | what it says |
|---|---|---|
| place | `\tnstack` and `\tnlayer`, or `\tngrid` | a block of slots, and the tensor in each |
| connect | `\tnconnect` | every index the block's layout implies |
| open, join | `\tnopen`, `\tnopenswap`, `\tnjoin` | the other indices: open ones, crossed ones, ones between two ports |
| label | `\tnput`, `\tnmid`, `\tnframe` | text on what is not an open index, a frame around a group |
| between blocks | `\tneq`, `\tnapprox`, `\tnbreak` | a relation sign, or a new row |

## Step by step

One figure, built a command at a time in the examples' notation: on the left
the figure so far, what the step adds marked; on the right what it draws.
`canl`, `center`, `canr`, `gate` and `gauge` are the notation's declarations;
every other word is a command or a name the stack gave. Nothing in it is a
length or a coordinate, so two people who draw the same network write the
same file.

[the steps](steps/)

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
- **A list of names takes ranges.** Wherever a command takes tensors or
  ports, `S-ket-{2..4}` is `S-ket-2, S-ket-3, S-ket-4`, and the range may
  stand anywhere in the name (`P-{1..4}-2`, `S-b-{1..2}:right`).
- **What a layout decides, a type can say.** A stack gives a tensor an index
  on every side, one per site or layer it covers; a type that says
  `tn index={l:left, s:down}` has those indices, named, and no others. A
  command naming another is an error, and so is a picture that ends with one
  of them not drawn. Several may leave on one side, `{a:left, b:left}`, and
  two tensors side by side are joined index by index, in order. A port is
  then named by its index, `T:l`, or its place in the type's order, `T:1`, as
  well as by its side. A type is best declared with `\tntype`, which names
  it. `\tnshow` writes out what was made of a tensor.
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
| `<grid>-<i>-<j>-<nw/ne/se/sw>` | the end of a grid site's index of the lattice opened that way |
| `<grid>-<i>-<j>-top`, `-bottom`, `-left`, `-right` | the halves of a site of a `split` grid: top and bottom where i+j is even, left and right where it is odd |
| `<tensor>:<side>[:<n>]` | a port, for `\tnjoin` |
