#!/usr/bin/env bash
# Build examples/*.tex into examples/out/<name>.svg and .pdf (LuaLaTeX, pdftocairo).
#   scripts/build-examples.sh [examples/<name>.tex ...]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT=examples/out; BUILD=$(mktemp -d); trap 'rm -rf "$BUILD"' EXIT
mkdir -p "$OUT"
[ $# -gt 0 ] || set -- examples/*.tex
for src in "$@"; do
  name="$(basename "$src" .tex)"
  if ! TEXINPUTS="$ROOT/tex//:${TEXINPUTS:-}" lualatex -interaction=nonstopmode -halt-on-error \
      -output-directory="$BUILD" "$src" >/dev/null 2>&1; then
    echo "error: $src" >&2; grep -A4 '^!' "$BUILD/$name.log" >&2 || true; exit 1
  fi
  cp "$BUILD/$name.pdf" "$OUT/$name.pdf"
  pdftocairo -svg "$BUILD/$name.pdf" "$OUT/$name.svg"
  echo "$OUT/$name.svg"
done
