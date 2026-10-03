#!/usr/bin/env bash
# The git around scripts/publish.py, for the Documenter workflows.
#
#   scripts/gh-pages.sh checkout <dir>         the gh-pages branch into <dir>,
#                                              or a new empty one if it does
#                                              not exist yet
#   scripts/gh-pages.sh push <dir> <message>   commit everything in <dir> and
#                                              push it, if anything changed
#
# Run inside a checkout of the repository on a runner: it pushes with the
# workflow's own token, as github-actions[bot].
set -euo pipefail
cmd="$1" dir="$2"
remote="$(git config --get remote.origin.url)"
case "$cmd" in
  checkout)
    rm -rf "$dir"
    # the credentials actions/checkout left in this checkout, for the clone and
    # the push
    auth=()
    if header="$(git config --get "http.https://github.com/.extraheader")"; then
      auth=(-c "http.https://github.com/.extraheader=$header")
    fi
    if git ls-remote --exit-code --heads origin gh-pages >/dev/null 2>&1; then
      git "${auth[@]}" clone --quiet --depth 1 --branch gh-pages "$remote" "$dir"
    else
      git init --quiet "$dir"
      git -C "$dir" checkout --quiet --orphan gh-pages
      git -C "$dir" remote add origin "$remote"
    fi
    if [ -n "${header:-}" ]; then
      git -C "$dir" config "http.https://github.com/.extraheader" "$header"
    fi
    git -C "$dir" config user.name "github-actions[bot]"
    git -C "$dir" config user.email "41898282+github-actions[bot]@users.noreply.github.com"
    ;;
  push)
    git -C "$dir" add -A
    if git -C "$dir" diff --cached --quiet; then
      echo "gh-pages: nothing changed"; exit 0
    fi
    git -C "$dir" commit --quiet -m "$3"
    git -C "$dir" push --quiet origin HEAD:gh-pages
    echo "gh-pages: pushed"
    ;;
  *) echo "usage: scripts/gh-pages.sh checkout <dir> | push <dir> <message>" >&2; exit 2 ;;
esac
