# Agent Notes

- Use `PRD.md` as the product requirements source.
- Main entry point: `app/main.py`; core modules: `app/console.py`, `app/archive.py`, `app/storage.py`; tests: `app/tests/`.
- Run the CLI with `python app/main.py`.
- Run the full test suite with `python -m pytest`.
- Create PRs only after local CI passes.
- Target Python 3.13 and keep runtime code limited to the standard library.
- Before behavior changes, review `PRD.md` and nearby tests. Do not stage generated `data/` artifacts unless explicitly requested.
