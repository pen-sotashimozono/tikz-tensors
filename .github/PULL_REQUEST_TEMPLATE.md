## Why

<!-- What this changes and why; the diff already shows how. -->

## Version

<!-- scripts/version.py check says which step this needs; CI enforces it. -->

- [ ] No change under `tex/` or `theme/` — version unchanged
- [ ] `python3 scripts/version.py bump <patch|minor|major> "Why."` — CHANGELOG entry written

## Appearance

- [ ] `tests/run.sh` passes locally, or the change in appearance is intended and
      `tests/run.sh --update` refreshed `tests/reference/` (a minor step at least)
- [ ] A new style is drawn in `tests/cases/styles.tex` and listed in the README
