from dataclasses import dataclass
from pathlib import Path

from constants import MAX_ORDER
from utils import slugify

from ..errors import StorageError


@dataclass(frozen=True)
class MarkdownExportItem:
    directory: Path
    path: Path
    prompt: dict


def plan_markdown_export(prompts, data_dir):
    grouped_prompts = group_prompts_by_category(prompts)
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
            export_plan.append(MarkdownExportItem(directory, path, prompt))

    return export_plan


def group_prompts_by_category(prompts):
    grouped_prompts = []
    category_positions = {}
    for prompt in prompts:
        category = prompt["category"]
        if category not in category_positions:
            category_positions[category] = len(grouped_prompts)
            grouped_prompts.append((category, []))
        grouped_prompts[category_positions[category]][1].append(prompt)
    return grouped_prompts
