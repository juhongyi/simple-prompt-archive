import json
from dataclasses import dataclass
from pathlib import Path

from constants import MAX_ORDER
from utils import slugify

from .errors import StorageError
from .paths import data_directory


@dataclass(frozen=True)
class _MarkdownExportItem:
    directory: Path
    path: Path
    prompt: dict


def export_markdown(prompts, root=None):
    data_dir = data_directory(root)
    export_plan = _plan_markdown_export(prompts, data_dir)

    if not export_plan:
        _validate_data_directory(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        return []

    _validate_markdown_paths(data_dir, export_plan)

    data_dir.mkdir(parents=True, exist_ok=True)
    written_paths = []
    for item in export_plan:
        item.directory.mkdir(parents=True, exist_ok=True)
        item.path.write_text(_format_markdown_prompt(item.prompt), encoding="utf-8")
        written_paths.append(item.path)
    return written_paths


def _plan_markdown_export(prompts, data_dir):
    grouped_prompts = _group_prompts_by_category(prompts)
    if len(grouped_prompts) > MAX_ORDER:
        raise StorageError("카테고리 수는 9,999개를 초과할 수 없습니다.")

    export_plan = []
    for category_index, (category, category_prompts) in enumerate(
        grouped_prompts,
        start=1,
    ):
        if len(category_prompts) > MAX_ORDER:
            raise StorageError("카테고리별 프롬프트 수는 9,999개를 초과할 수 없습니다.")

        category_slug = slugify(str(category))
        if not category_slug:
            raise StorageError("카테고리 slug가 비어 있습니다.")

        directory = data_dir / f"{category_index:04d}-{category_slug}"
        for prompt_index, prompt in enumerate(category_prompts, start=1):
            prompt_slug = slugify(str(prompt["title"]))
            if not prompt_slug:
                raise StorageError("프롬프트 slug가 비어 있습니다.")
            path = directory / f"{prompt_index:04d}-{prompt_slug}.md"
            export_plan.append(_MarkdownExportItem(directory, path, prompt))

    return export_plan


def _validate_markdown_paths(data_dir, export_plan):
    _validate_data_directory(data_dir)

    for item in export_plan:
        if item.directory.exists() and not item.directory.is_dir():
            raise StorageError("필요한 폴더 위치에 파일이 있습니다.")
        if item.path.exists() and not item.path.is_file():
            raise StorageError("필요한 파일 위치에 폴더가 있습니다.")


def _validate_data_directory(data_dir):
    if data_dir.exists() and not data_dir.is_dir():
        raise StorageError("data 위치에 파일이 있어 내보낼 수 없습니다.")


def _group_prompts_by_category(prompts):
    grouped_prompts = []
    category_positions = {}
    for prompt in prompts:
        category = prompt["category"]
        if category not in category_positions:
            category_positions[category] = len(grouped_prompts)
            grouped_prompts.append((category, []))
        grouped_prompts[category_positions[category]][1].append(prompt)
    return grouped_prompts


def _format_markdown_prompt(prompt):
    return (
        "---\n"
        f"title: {_quote_frontmatter(prompt['title'])}\n"
        f"category: {_quote_frontmatter(prompt['category'])}\n"
        f"favorite: {str(prompt['favorite']).lower()}\n"
        f"usage_count: {prompt['usage_count']}\n"
        "---\n\n"
        f"{prompt['content']}"
    )


def _quote_frontmatter(value):
    return json.dumps(str(value), ensure_ascii=False)
