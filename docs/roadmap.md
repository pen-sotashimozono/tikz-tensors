# Roadmap: every algorithm, written one way

The goal is that each algorithm on tensornetwork.org (DMRG, TEBD, TDVP, zip-up,
TRG, CTMRG, MERA, ...) can be drawn in this package's notation, and that two
people (or two LLM runs) who draw the same algorithm write **the same file**.
That second part is what `gofmt` gives Go, and Go gets it from a tool rather
than from good intentions. So this plan has two halves: the **vocabulary** each
algorithm needs, and the **rules and the checker** that leave one way to use it.

Nothing here is released. It is a proposal, to be cut into minor versions.

The examples are a test of the vocabulary, not a catalogue of algorithms: each
draws one object an algorithm uses (an effective Hamiltonian, a transfer-matrix
fixed point, an expectation value) and is named for that object, so that one
file serves every algorithm that uses it.

## Where the freedom is today

The examples already agree on colour and shape — the canonical-form palette is
the settled part. Where they diverge is geometry. Counting the free choices in
the current examples:

| file | lengths written by hand | raw `\node` / `\draw` |
|---|---|---|
| `06-dmrg` (now `14-heff-two-site`) | `\tnGap`, `\tnThetaY`, `\tnThetaH`, `7mm`, `31mm` | `\tikzset{env/...}` local style |
| `07-fixed-point` | `34mm`, `44mm`, `10.5mm`, `14.5mm`, `0.95`, `1.6`, `1.05`, `1.45`, `3.5`, `4.4`, `6.4cm`, `4.8cm` | 12 raw `\node`s, `=` placed by hand |
| `08-tebd` | `x=1.45cm`, `52mm`, `92mm`, `9 ... 79 mm`, `7.6cm` | local `\tebdchain` macro |
| `09-expectation` | `x=1.25cm`, `-4.15`, `8mm`, `28.5mm`, `-2.2`, `9mm` | raw `\node[op]` |

Every one of those numbers is a place where a second author picks a different
number, and an LLM picks a different one on each run. Colour is not where the
files drift; layout is.

## The rules

These are the `gofmt` of the package, checked by `tests/lint.py` rather than
left to review. Rules 1–4 are checked now, together with a fixed frame (the
standard preamble and one bare `tikzpicture`) and one spelling for a layer (a
run of like entries is one `<n>*<entry>`); 5 and 6 are about commands that do
not exist yet and arrive in the linter with them.

1. **No lengths in a figure.** An example states topology and roles; the
   package owns every distance: the site pitch, the layer gap, the stub length
   of an open index, the drop of a physical leg, the gap before `=`. A figure
   contains integers (site numbers, counts) and no `mm`, `cm`, `pt` or decimal.
   A figure that needs a length is a missing token, and the fix goes in `tex/`.
2. **Every tensor has a role, and the role is the whole style.** No `fill=`,
   `draw=`, `minimum ...=`, `shape=` in a figure. The package names only
   shapes; a role is a style of the author's notation file
   (`examples/conventions/notation.tex` for this repository), which decides
   shape and colour together. A figure names roles, never shapes and colours.
3. **One command per concept.** No raw `\node`, `\draw`, `\path`, `scope`
   shifts, `\tikzset` or `\newcommand` in a figure. Labels go through `\tnput`
   and `\tnmid`. A pattern a figure needs twice is a command in `tex/`.
4. **Positions are lattice points.** A tensor sits at a (site, layer) slot of
   a stack, or a (column, row) slot of a grid, never at a coordinate.
5. **Names are fixed.** Layers are `ket`, `op`, `bra` (and `op2`, ... for more
   operators); node names are derived (`<stack>-<layer><site>`), not chosen.
6. **One order of statements**: placement, then bonds, then open legs, then
   labels. The linter checks the order, which is what makes a diff between two
   authors' files small.

The legacy examples fail these. The linter runs as a ratchet: a file listed in
`tests/lint-legacy.txt` is exempt, the list may only shrink, and an example
leaves it when it is rewritten on the new commands.

## Algorithms, and what each needs

From the tensornetwork.org index (MPS, PEPS, tree and MERA, renormalisation,
decompositions). "Needs" is what the package lacks for that picture.

| algorithm | picture | needs |
|---|---|---|
| SVD, QR | T = U S V†, T = Q R | `iso` at any angle; equation layout |
| canonical form | `08-canonical`, `09-center` | — (done) |
| DMRG (two-site) | H_eff, `14-heff-two-site` | **stack**, **env**, open stubs |
| TEBD | `17-trotter-sweep` | gate drop as a token, not `9 ... 79 mm` |
| TDVP | forward on AC, backward on C | stack, env, `centerbond` in a stack |
| MPO × MPS, naive | two layers fused | stack, **fused index** |
| zip-up | left: new MPS, zipper, right: two layers | stack, fused index, SVD split |
| density-matrix algorithm | ket, W, W†, bra, traced | four-layer stack, env |
| fitting | ⟨φ\|W\|ψ⟩ with envs | stack, env |
| expectation value | `13-expectation` | stack (the hand-placed `-4.15`, `28.5mm` go) |
| iDMRG, VUMPS | AL, AC, C, AR; fixed points | stack, env, equation layout (`18-fixed-point`) |
| sampling | ψ with legs capped by basis vectors | **cap** (a vector on an index) |
| TTN | tree, isometric toward the root | `iso` at any angle, tree placement |
| MERA | disentanglers u, isometries w | `iso` 2→1, gate as disentangler |
| PEPS, simple update | 2D grid, λ on bonds | **grid**, physical legs out of the plane |
| boundary MPS, CTMRG | corners C, edges T, projectors | grid, **env corner/edge** roles |
| TRG, HOTRG | T split into S on diagonals; U merging two legs | rotated grid, `iso` at any angle |
| TNR | disentanglers and isometries in 2D | grid, `iso`, gate |

Ranked by how many rows they unblock:

1. **stack** — layers `ket`/`op`/`bra` in one column grid, the layer gap a
   token. Nine algorithms, and the source of most numbers in `14-heff-two-site`, `18-fixed-point`, `13-expectation`.
2. **env** — the contracted remainder of a network: L and R blocks, the
   fixed points l and r, CTM corners and edges. It spans the layers of a stack
   and gives each layer one leg at that layer's height (today `[yshift=10.5mm]`).
   This is not the `env` removed in v0.3.0, which put an object at the end of a
   finite chain; this one is a contraction that exists in the algorithm.
3. **open stubs and equations** — `\tnopen` with a standard stub length and a
   direction, and an equation row that places `=`, `\lambda`, `+` between
   diagrams at a standard gap.
4. **`iso` at any angle** — the triangle as "isometric toward there". Trees,
   MERA, TRG, QR and the projectors of CTMRG all need it; `canl` and `canr`
   become the two horizontal cases of it.
5. **grid** — 2D placement, including the 45° grid TRG turns into.
6. **small primitives** — `delta` (copy tensor, an ink dot), `cap` (a basis
   vector on an index, for sampling and product states), fused index (two bonds
   merged, for MPO × MPS), trace loop (`\tnjoin`, v0.9.0).

## Colour: closing the role table

Decided so far: stay inside the ramp as it is and extend it only when a role
cannot be said with it. The palette works because each colour is a role and not a decoration. Today the
roles are a chain's: `canl`, `canr`, `center`, `mpo`, `gate`, `coef`. The other
algorithms bring roles that do not have a colour yet, and the open decisions
are these:

| new role | used by | proposal | open question |
|---|---|---|---|
| env | DMRG, TDVP, fitting, VUMPS, CTMRG | **decided**: `purple1` at 25%, one colour for L and R; the gate moved to `yellow1` | — |
| isometry, not on a chain | TTN, MERA w, TRG S, HOTRG U, CTMRG P | `canl`'s colour for "isometric toward the center", whatever the angle | in a tree there is no left and right, so one colour; is `canr` then only the 1D mirror? |
| disentangler | MERA u, TNR | `gate` (it is a unitary on two indices) | — |
| partition-function T | TRG, HOTRG | `coef` (a plain array) | — |
| delta / copy | MPO, CP, TRG | ink dot, no fill | — |
| updated vs not yet | zip-up, fitting sweeps | a step darker on the same scale | worth showing, or left to the caption? |

Also to settle: `coef` draws in `black!6`, not in the `coef` colour token, which
`tokens.toml` defines as `blue1` (the same as `canl`). One of the two should go.

## Phases

Each phase is a minor version, ships its examples, and takes the examples it
touches off the lint ratchet.

| phase | adds | examples |
|---|---|---|
| 0 | `tests/lint.py` (the rules), `tests/lint-legacy.txt`, CI step — **done** | — |
| 1 | stack, env, `\tnopen`, `\tneq` — **done** (v0.5.0) | `14-heff-two-site`, `13-expectation` rewritten; single-site and bond H_eff, fixed point, low rank |
| 2 | fused index (`tn double`), delta (`tn dot`), basis caps, tensors across layers, `\|` and `dots` slots, rows — **done** (v0.6.0) | MPO × MPS, zip-up, CP, sampling (`11-mpo-mps`, `12-zip-up`, `04-cp`, `10-sampling`); every legacy example rewritten |
| 3 | triangles up and down, one rule for vertical indices, `tn single` — **done** (v0.7.0) | SVD/QR, TTN, MERA (`03-svd-qr`, `19-ttn`, `20-mera`), |
| 4 | `\tngrid`, environment corners and sides — **done** (v0.8.0) | PEPS, simple update, CTMRG, HOTRG (`21-peps`, `22-simple-update`, `23-ctmrg`, `24-hotrg`); TRG still needs diagonal indices |
| 4½ | modules (core, nodes, edges, canvas, stack, connect, grid, labels); a tensor's indices as ports; `\tnjoin`; `<n>*` in a layer; `\tnset`; the coordinate commands removed — **done** (v0.9.0) | periodic MPS (`07-periodic-mps`) |
| 4¾ | folders (`core/`, `style/`, `layout/`); the abstract layout, with stack, tree and grid as layouts; ports recorded once drawn — **done** (v0.10.0) | the grid on `\tnconnect`/`\tnopen` (`21-peps`, `22-simple-update`); TRG is next: a layout of its own |
| 5 | machine learning | neural networks as diagrams: what is a tensor (weights, feature maps) and what is not (activations) |

## What a figure looks like after phase 1

The shape of the API, not its final spelling. The top-left equation of `18-fixed-point`,
the transfer-matrix fixed point, today is 12 lines with 9 numbers. Written on
a stack:

```latex
\begin{tikzpicture}
  \tnstack{X}{ket, bra}{canl/$A$, canl/$\bar A$}  % one site, two layers
  \tnenv[left]{X}{$l$}                            % spans both, one leg each
  \tnopen[right]{X}                               % every layer's last site
  \tnequals{$\lambda$}                            % the next stack starts here
  \tnstack{Y}{ket, bra}{}                         % no sites: the env alone
  \tnenv[left]{Y}{$l$}
  \tnopen[right]{Y}
\end{tikzpicture}
```

No number in it, and nothing in it that a second author would spell another way.
