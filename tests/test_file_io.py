import json

import pytest

from prompt_archive.markdown_export import MarkdownExportError, export_markdown, slugify
from prompt_archive.storage import JSONImportError, export_json, import_json, replace_prompts_from_json


def prompt(
    title: str = "Better title",
    content: str = "Prompt body",
    category: str = "Writing",
    favorite: bool = False,
    usage_count: int = 0,
) -> dict[str, object]:
    return {
        "title": title,
        "content": content,
        "category": category,
        "favorite": favorite,
        "usage_count": usage_count,
    }


def test_export_json_writes_versioned_prompt_document(tmp_path) -> None:
    path = tmp_path / "data" / "prompts.json"
    prompts = [prompt(favorite=True, usage_count=3)]

    export_json(prompts, path)

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "version": 1,
        "prompts": [
            {
                "title": "Better title",
                "content": "Prompt body",
                "category": "Writing",
                "favorite": True,
                "usage_count": 3,
            }
        ],
    }


def test_import_json_replaces_current_prompts_only_after_validation(tmp_path) -> None:
    path = tmp_path / "data" / "prompts.json"
    replacement = [prompt(title="Imported", content="Imported body", category="Imported category")]
    export_json(replacement, path)
    prompts = [prompt(title="Existing")]

    replace_prompts_from_json(prompts, path)

    assert prompts == replacement


def test_import_json_rejects_invalid_documents_and_preserves_memory(tmp_path) -> None:
    path = tmp_path / "data" / "prompts.json"
    path.parent.mkdir()
    path.write_text(json.dumps({"version": 2, "prompts": []}), encoding="utf-8")
    prompts = [prompt(title="Existing")]

    with pytest.raises(JSONImportError):
        replace_prompts_from_json(prompts, path)

    assert prompts == [prompt(title="Existing")]


def test_import_json_requires_all_prompt_fields(tmp_path) -> None:
    path = tmp_path / "prompts.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "prompts": [
                    {
                        "title": "Missing field",
                        "content": "Body",
                        "category": "Writing",
                        "favorite": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(JSONImportError):
        import_json(path)


def test_slugify_keeps_hangul_ascii_letters_and_digits() -> None:
    assert slugify("Better title!") == "better-title"
    assert slugify("한글 Prompt!! 42") == "한글-prompt-42"
    assert slugify("***") == ""


def test_export_markdown_writes_category_directories_and_frontmatter(tmp_path) -> None:
    prompts = [
        prompt(
            title='Quote " and \\ slash\nline',
            content="본문 전체",
            category="Writing Tools",
            favorite=True,
            usage_count=7,
        ),
        prompt(title="Image idea", content="Image body", category="Images"),
        prompt(title="Second writing", content="More body", category="Writing Tools"),
    ]

    written = export_markdown(prompts, tmp_path / "data")

    assert [path.relative_to(tmp_path / "data").as_posix() for path in written] == [
        "0001-writing-tools/0001-quote-and-slash-line.md",
        "0002-images/0001-image-idea.md",
        "0001-writing-tools/0002-second-writing.md",
    ]
    first_file = (tmp_path / "data" / "0001-writing-tools" / "0001-quote-and-slash-line.md").read_text(
        encoding="utf-8"
    )
    assert first_file == (
        "---\n"
        'title: "Quote \\" and \\\\ slash\\nline"\n'
        'category: "Writing Tools"\n'
        "favorite: true\n"
        "usage_count: 7\n"
        "---\n"
        "\n"
        "본문 전체\n"
    )


def test_export_markdown_with_no_prompts_creates_only_output_directory(tmp_path) -> None:
    output_dir = tmp_path / "data"

    assert export_markdown([], output_dir) == []
    assert output_dir.is_dir()
    assert list(output_dir.iterdir()) == []


def test_export_markdown_rejects_empty_slugs_without_filesystem_changes(tmp_path) -> None:
    output_dir = tmp_path / "data"

    with pytest.raises(MarkdownExportError):
        export_markdown([prompt(title="***", category="Writing")], output_dir)

    assert not output_dir.exists()


def test_export_markdown_rejects_path_conflicts_before_writing(tmp_path) -> None:
    output_dir = tmp_path / "data"
    output_dir.mkdir()
    (output_dir / "0001-writing").write_text("not a directory", encoding="utf-8")

    with pytest.raises(MarkdownExportError):
        export_markdown([prompt(category="Writing")], output_dir)

    assert (output_dir / "0001-writing").read_text(encoding="utf-8") == "not a directory"


def test_export_markdown_rejects_file_path_directory_conflict_before_writing(tmp_path) -> None:
    output_dir = tmp_path / "data"
    conflicting_file_path = output_dir / "0001-writing" / "0001-better-title.md"
    conflicting_file_path.mkdir(parents=True)

    with pytest.raises(MarkdownExportError):
        export_markdown([prompt(category="Writing")], output_dir)

    assert conflicting_file_path.is_dir()
    assert list(conflicting_file_path.iterdir()) == []


def test_export_markdown_rejects_too_many_categories_without_filesystem_changes(tmp_path) -> None:
    output_dir = tmp_path / "data"
    prompts = [prompt(title=f"Prompt {index}", category=f"Category {index}") for index in range(10_000)]

    with pytest.raises(MarkdownExportError):
        export_markdown(prompts, output_dir)

    assert not output_dir.exists()


def test_export_markdown_rejects_too_many_prompts_in_category_without_filesystem_changes(tmp_path) -> None:
    output_dir = tmp_path / "data"
    prompts = [prompt(title=f"Prompt {index}", category="Writing") for index in range(10_000)]

    with pytest.raises(MarkdownExportError):
        export_markdown(prompts, output_dir)

    assert not output_dir.exists()
