from ..paths import data_directory
from .formatting import format_markdown_prompt
from .planning import plan_markdown_export
from .validation import validate_data_directory, validate_markdown_paths


def export_markdown(prompts, root=None):
    data_dir = data_directory(root)
    export_plan = plan_markdown_export(prompts, data_dir)

    if not export_plan:
        validate_data_directory(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        return []

    validate_markdown_paths(data_dir, export_plan)

    data_dir.mkdir(parents=True, exist_ok=True)
    written_paths = []
    for item in export_plan:
        item.directory.mkdir(parents=True, exist_ok=True)
        item.path.write_text(format_markdown_prompt(item.prompt), encoding="utf-8")
        written_paths.append(item.path)
    return written_paths
