#!/usr/bin/env bash
# The package's tests: every example and test case compiles, and looks as it did.
#
#   tests/run.sh            # compile with LuaLaTeX and pdfLaTeX, compare the pictures
#   tests/run.sh --update   # the same, then take the new pictures as the references
#
# 1. examples/*.tex and tests/cases/*.tex compile with both engines, with no
#    warning from LaTeX or a package and the log naming this version of the
#    package (the \ProvidesPackage line, as scripts/version.py reads it).
# 2. tests/coverage.py: every style and command in tex/ is used by some case.
# 3. The LuaLaTeX pages, rendered by pdftoppm, match tests/reference/*.png
#    (tests/compare.py). A deliberate change in appearance is --update plus a
#    minor version step, which scripts/version.py check enforces.
#
# Output goes to tests/out/ (gitignored): <engine>/<name>.pdf and .log, and
# rendered/<name>.png with a <name>-diff.png beside any page that changed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT=tests/out
rm -rf "$OUT"
mkdir -p "$OUT/rendered"
export TEXINPUTS="$ROOT/tex//:${TEXINPUTS:-}"
VERSION="$(python3 scripts/version.py)"
fail=0

for engine in lualatex pdflatex; do
  mkdir -p "$OUT/$engine"
  for src in examples/*.tex tests/cases/*.tex; do
    name="$(basename "$src" .tex)"
    log="$OUT/$engine/$name.log"
    if ! "$engine" -interaction=nonstopmode -halt-on-error -output-directory="$OUT/$engine" \
        "$src" >/dev/null 2>&1; then
      echo "FAIL  $engine $src: does not compile"
      grep -A6 '^!' "$log" || tail -20 "$log"
      fail=1
      continue
    fi
    # A one-pass build: "rerun" notices (hyperref's .out, labels) are expected.
    warnings="$(grep -E '(LaTeX|Package [^ ]+) Warning' "$log" \
      | grep -vE 'rerunfilecheck|Rerun to get|may have changed' || true)"
    if [ -n "$warnings" ]; then
      echo "FAIL  $engine $src: warnings"
      echo "$warnings" | sed 's/^/      /'
      fail=1
    elif ! grep -Eq "^Package: tikz-tensors [0-9/]+ v$VERSION " "$log"; then
      echo "FAIL  $engine $src: the log does not show tikz-tensors v$VERSION"
      fail=1
    else
      echo "  ok  $engine $src"
    fi
  done
done

python3 tests/coverage.py || fail=1

for pdf in "$OUT"/lualatex/*.pdf; do
  # 180 dpi, because poppler's Splash backend snaps a thin axis-aligned stroke
  # to whole pixels without anti-aliasing: where a stroke is not a whole number
  # of them, two strokes of the same width round differently by where each
  # lands. At 150 dpi 0.8pt is 1.67 px and the five legs of 05-centre came out
  # 0.8, 0.8, 1.6, 1.6, 1.6 in ink -- half of them twice the weight of the
  # others, plainly visible. 0.8pt is whole at every multiple of 90, and
  # measured there the legs are uniform (180, 270, 360) and ragged between
  # (150, 200, 300). 180 is the cheapest of them: 2 px a stroke, references
  # 330K against 228K, compare.py about three seconds slower.
  #
  # This fixes the widths, not the phase effect itself: a width that is not
  # whole at 180 is ragged again, which is why the one demo of `tn line width'
  # is 1.6pt (4 px) and not 1.8pt (4.5 px). pdftocairo anti-aliases and avoids
  # the whole business, but its anti-aliasing differs between poppler versions
  # and references made here then failed against the runner's; this test exists
  # to be reproducible, and snapping is.
  pdftoppm -r 180 -png -singlefile "$pdf" "$OUT/rendered/$(basename "$pdf" .pdf)"
done
python3 tests/compare.py "$OUT/rendered" "$@" || fail=1
exit "$fail"
