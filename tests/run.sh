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
# 3. The LuaLaTeX pages, rendered by pdftocairo, match tests/reference/*.png
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
  # pdftocairo, not pdftoppm. poppler's own Splash backend snaps a thin
  # axis-aligned stroke to whole pixels and does not anti-alias it, so the two
  # horizontal edges of a box round independently by where each lands and can
  # come out a pixel apart -- a box with a heavier bottom than top. It is a
  # phase effect, not a resolution one: measured on one page at fourteen
  # resolutions it flips on and off with no rule (clean at 150, 180, 330, 360;
  # a pixel out at 240, 270, 300, 450), and it depends on where the box sits,
  # so no choice of dpi is safe for every figure. Cairo anti-aliases instead
  # and the two edges agree to a few per cent. Both write 8-bit RGB at the same
  # size, so compare.py and the references carry over unchanged.
  pdftocairo -png -r 150 -singlefile "$pdf" "$OUT/rendered/$(basename "$pdf" .pdf)"
done
python3 tests/compare.py "$OUT/rendered" "$@" || fail=1
exit "$fail"
