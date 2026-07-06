import json
from dataclasses import dataclass
from pathlib import Path

VERSION = 1
STANDARD_FIELDS = ("title", "content", "category", "favorite", "usage_count")
MAX_ORDER = 9999


class StorageError(Exception):
    pass


@dataclass(frozen=True)
class _MarkdownExportItem:
    directory: Path
    path: Path
    prompt: dict


def project_root():
    return Path(__file__).resolve().parents[1]


def data_directory(root=None):
    return Path(root if root is not None else project_root()) / "data"


def json_file_path(root=None):
    return data_directory(root) / "prompts.json"


def standard_prompt(prompt):
    return {field: prompt[field] for field in STANDARD_FIELDS}


def export_json(prompts, root=None):
    path = json_file_path(root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(_json_payload(prompts), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise StorageError("JSON 파일을 쓸 수 없습니다.") from exc
    return path


def import_json(root=None):
    path = json_file_path(root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise StorageError("JSON 파일을 읽을 수 없습니다.") from exc
    except json.JSONDecodeError as exc:
        raise StorageError("JSON 형식이 올바르지 않습니다.") from exc

    if payload.get("version") != VERSION:
        raise StorageError("지원하지 않는 JSON 버전입니다.")
    prompts = payload.get("prompts")
    if not isinstance(prompts, list):
        raise StorageError("prompts 배열이 없습니다.")

    for prompt in prompts:
        if not isinstance(prompt, dict):
            raise StorageError("프롬프트 항목은 객체여야 합니다.")
        missing_fields = [field for field in STANDARD_FIELDS if field not in prompt]
        if missing_fields:
            raise StorageError("프롬프트 항목에 필수 필드가 없습니다.")

    return [dict(prompt) for prompt in prompts]


def slugify(value):
    slug_parts = []
    in_separator = False

    for char in value.strip():
        if _is_allowed_slug_char(char):
            slug_parts.append(char.lower())
            in_separator = False
        elif not in_separator:
            slug_parts.append("-")
            in_separator = True

    return "".join(slug_parts).strip("-")


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


def _json_payload(prompts):
    return {
        "version": VERSION,
        "prompts": [standard_prompt(prompt) for prompt in prompts],
    }


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


def _is_allowed_slug_char(char):
    return (
        "0" <= char <= "9"
        or "a" <= char <= "z"
        or "A" <= char <= "Z"
        or "\uac00" <= char <= "\ud7a3"
    )
