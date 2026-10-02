#!/usr/bin/env bash
# The package's tests: every example and test case compiles, follows the rules,
# and looks as it did.
#
#   tests/run.sh                    # all of it, as a contributor runs it
#   tests/run.sh --update           # the same, then take the new pictures as the references
#   tests/run.sh compile <engine>   # 1 for one engine (lualatex or pdflatex)
#   tests/run.sh rules              # 2
#   tests/run.sh compare [--update] # 3, on the LuaLaTeX PDFs already in tests/out/
#
# 1. examples/*.tex and tests/cases/*.tex compile, with no warning from LaTeX or
#    a package and the log naming this version of the package (the
#    \ProvidesPackage line, as scripts/version.py reads it).
# 2. tests/coverage.py: every style and command in tex/ is used by some case;
#    tests/lint.py: every example follows the figure rules (docs/roadmap.md).
# 3. The LuaLaTeX pages, as SVG from pdftocairo, draw what tests/reference/*.svg
#    draws (tests/compare.py). A deliberate change in appearance is --update
#    plus a minor version step, which scripts/version.py check enforces.
#
# CI runs each step as its own job (.github/workflows/ci.yml): the two engines
# on two runners, the rules with no TeX at all, and the comparison, in the job
# named test, on the LuaLaTeX job's PDFs. Run with no step, this does all of
# them in order.
#
# Output goes to tests/out/ (gitignored): <engine>/<name>.pdf and .log, and
# rendered/<name>.svg with a <name>-diff.txt beside any page that changed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT=tests/out
export TEXINPUTS="$ROOT/tex//:$ROOT/examples/conventions//:${TEXINPUTS:-}"

compile() {
  local engine="$1" fail=0 version name log warnings
  version="$(python3 scripts/version.py)"
  rm -rf "$OUT/$engine"
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
    elif ! grep -Eq "^Package: tikz-tensors [0-9/]+ v$version " "$log"; then
      echo "FAIL  $engine $src: the log does not show tikz-tensors v$version"
      fail=1
    else
      echo "  ok  $engine $src"
    fi
  done
  return "$fail"
}

rules() {
  local fail=0
  python3 tests/coverage.py || fail=1
  python3 tests/lint.py || fail=1
  return "$fail"
}

compare() {
  # SVG, not pixels: a rasteriser snaps thin strokes to whole pixels and
  # anti-aliases differently from one poppler to the next, so a picture had
  # to be compared with a tolerance in pixels that a moved leg could hide in.
  # pdftocairo's SVG is the drawing itself -- every path and glyph, in pt --
  # and compare.py matches it thing by thing.
  rm -rf "$OUT/rendered"
  mkdir -p "$OUT/rendered"
  for pdf in "$OUT"/lualatex/*.pdf; do
    pdftocairo -svg "$pdf" "$OUT/rendered/$(basename "$pdf" .pdf).svg"
  done
  python3 tests/compare.py "$OUT/rendered" "$@"
}

case "${1:-all}" in
  compile) compile "$2" ;;
  rules)   rules ;;
  compare) shift; compare "$@" ;;
  all|--update)
    fail=0
    compile lualatex || fail=1
    compile pdflatex || fail=1
    rules || fail=1
    compare "$@" || fail=1
    exit "$fail" ;;
  *) echo "usage: tests/run.sh [--update | compile <engine> | rules | compare [--update]]" >&2
     exit 2 ;;
esac
