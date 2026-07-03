from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prompt_archive.prompts import Prompt


DEFAULT_JSON_PATH = Path("data/prompts.json")
JSON_VERSION = 1
PROMPT_FIELDS = {"title", "content", "category", "favorite", "usage_count"}


class JSONImportError(ValueError):
    pass


def export_json(prompts: list[Prompt], path: Path | str = DEFAULT_JSON_PATH) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    document = {"version": JSON_VERSION, "prompts": prompts}
    target.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_json(path: Path | str = DEFAULT_JSON_PATH) -> list[Prompt]:
    target = Path(path)
    try:
        document = json.loads(target.read_text(encoding="utf-8"))
    except OSError as error:
        raise JSONImportError(str(error)) from error
    except json.JSONDecodeError as error:
        raise JSONImportError("JSON file is not valid") from error

    _validate_document(document)
    return list(document["prompts"])


def replace_prompts_from_json(prompts: list[Prompt], path: Path | str = DEFAULT_JSON_PATH) -> None:
    imported = import_json(path)
    prompts[:] = imported


def _validate_document(document: Any) -> None:
    if not isinstance(document, dict):
        raise JSONImportError("JSON root must be an object")
    if document.get("version") != JSON_VERSION:
        raise JSONImportError("JSON version must be 1")
    if "prompts" not in document or not isinstance(document["prompts"], list):
        raise JSONImportError("JSON prompts must be a list")
    for prompt in document["prompts"]:
        if not isinstance(prompt, dict):
            raise JSONImportError("Each prompt must be an object")
        if not PROMPT_FIELDS.issubset(prompt):
            raise JSONImportError("Each prompt must include all required fields")
