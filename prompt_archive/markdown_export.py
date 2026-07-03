from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from prompt_archive.prompts import Prompt, get_categories


MAX_ORDER = 9_999


class MarkdownExportError(ValueError):
    pass


@dataclass(frozen=True)
class MarkdownFile:
    path: Path
    prompt: Prompt


def slugify(value: str) -> str:
    parts = []
    previous_dash = False
    for character in value:
        if _is_allowed_slug_character(character):
            parts.append(character.lower())
            previous_dash = False
        elif not previous_dash:
            parts.append("-")
            previous_dash = True
    return "".join(parts).strip("-")


def export_markdown(prompts: list[Prompt], output_dir: Path | str = Path("data")) -> list[Path]:
    target_dir = Path(output_dir)
    files = _build_export_plan(prompts, target_dir)
    _validate_paths(target_dir, files)
    target_dir.mkdir(parents=True, exist_ok=True)
    for directory in _planned_directories(files):
        directory.mkdir(parents=True, exist_ok=True)
    for file in files:
        file.path.write_text(_render_markdown(file.prompt), encoding="utf-8")
    return [file.path for file in files]


def _build_export_plan(prompts: list[Prompt], output_dir: Path) -> list[MarkdownFile]:
    categories = get_categories(prompts)
    if len(categories) > MAX_ORDER:
        raise MarkdownExportError("Markdown export supports at most 9,999 categories")

    category_counts: dict[str, int] = defaultdict(int)
    category_orders = {category: index for index, category in enumerate(categories, start=1)}
    category_slugs = {}
    for category in categories:
        slug = slugify(str(category))
        if not slug:
            raise MarkdownExportError("Category slug cannot be empty")
        category_slugs[category] = slug

    files = []
    for prompt in prompts:
        category = prompt["category"]
        category_counts[category] += 1
        prompt_order = category_counts[category]
        if prompt_order > MAX_ORDER:
            raise MarkdownExportError("Markdown export supports at most 9,999 prompts per category")
        prompt_slug = slugify(str(prompt["title"]))
        if not prompt_slug:
            raise MarkdownExportError("Prompt slug cannot be empty")
        category_order = category_orders[category]
        category_slug = category_slugs[category]
        path = (
            output_dir
            / f"{category_order:04d}-{category_slug}"
            / f"{prompt_order:04d}-{prompt_slug}.md"
        )
        files.append(MarkdownFile(path=path, prompt=prompt))
    return files


def _validate_paths(output_dir: Path, files: list[MarkdownFile]) -> None:
    if output_dir.exists() and not output_dir.is_dir():
        raise MarkdownExportError("Markdown output path exists and is not a directory")
    for directory in _planned_directories(files):
        if directory.exists() and not directory.is_dir():
            raise MarkdownExportError(f"{directory} exists and is not a directory")
    for file in files:
        if file.path.exists() and file.path.is_dir():
            raise MarkdownExportError(f"{file.path} exists and is not a file")


def _planned_directories(files: list[MarkdownFile]) -> list[Path]:
    directories = []
    seen = set()
    for file in files:
        directory = file.path.parent
        if directory not in seen:
            directories.append(directory)
            seen.add(directory)
    return directories


def _render_markdown(prompt: Prompt) -> str:
    return (
        "---\n"
        f"title: {_quoted(prompt['title'])}\n"
        f"category: {_quoted(prompt['category'])}\n"
        f"favorite: {str(prompt['favorite']).lower()}\n"
        f"usage_count: {prompt['usage_count']}\n"
        "---\n"
        "\n"
        f"{prompt['content']}\n"
    )


def _quoted(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def _is_allowed_slug_character(character: str) -> bool:
    return (
        "a" <= character <= "z"
        or "A" <= character <= "Z"
        or "0" <= character <= "9"
        or "\uac00" <= character <= "\ud7a3"
    )
