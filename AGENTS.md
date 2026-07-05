# Agent Notes

- Use `PRD.md` as the product requirements source.
- Main entry point: `app/main.py`; core modules: `app/console.py`, `app/archive.py`, `app/storage.py`; tests: `app/tests/`.
- Run the CLI with `uv run python app/main.py`.
- Run the full test suite with `uv run pytest`.
- Target Python `>=3.13`; keep runtime dependencies empty. Pytest is the dev test dependency.
- Before behavior changes, review `PRD.md` and nearby tests. Do not stage generated `data/` artifacts unless explicitly requested.
- Break work into the smallest practical units, keep each commit focused, and commit only after the full test suite passes.
