# Simple Prompt Archive 📚

Simple Prompt Archive is a small console tool for saving, finding, and reusing
your favorite AI prompts.

## Requirements

- Python 3.13

## Run

```sh
python app/main.py
```

If you use uv, run:

```sh
uv run python app/main.py
```

## What You Can Do ✨

Use the numbered menu to:

- Add, list, search, and view prompt details.
- Browse prompts by category or favorites.
- Mark prompts as favorites.
- Edit or delete saved prompts.
- Sort prompts by usage count.
- Export and import prompts as JSON.
- Export prompts as Markdown files.

## Data Files 💾

The app keeps changes in memory while it runs. Use the export and import menu
items when you want to save or reload data.

- JSON export/import uses `data/prompts.json`.
- Markdown export writes files under `data/`.
