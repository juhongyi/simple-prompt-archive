import json
from pathlib import Path

import pytest
import storage


def test_export_json_writes_standard_schema_and_drops_extra_fields(
    tmp_path: Path,
) -> None:
    prompts = [
        {
            "title": "제목",
            "content": "본문",
            "category": "writing",
            "favorite": True,
            "usage_count": 3,
            "unknown": "kept only in memory",
        }
    ]

    path = storage.export_json(prompts, tmp_path)

    assert path == tmp_path / "data" / "prompts.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "version": 1,
        "prompts": [
            {
                "title": "제목",
                "content": "본문",
                "category": "writing",
                "favorite": True,
                "usage_count": 3,
            }
        ],
    }


def test_export_json_reports_filesystem_failures_as_storage_error(
    tmp_path: Path,
) -> None:
    (tmp_path / "data").write_text("not a directory", encoding="utf-8")

    with pytest.raises(storage.StorageError):
        storage.export_json([], tmp_path)


def test_import_json_replaces_with_file_order_and_preserves_extra_fields(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "prompts.json").write_text(
        json.dumps(
            {
                "version": 1,
                "prompts": [
                    {
                        "title": "first",
                        "content": "body",
                        "category": "writing",
                        "favorite": False,
                        "usage_count": 0,
                        "source": "external",
                    },
                    {
                        "title": "second",
                        "content": "body",
                        "category": "image",
                        "favorite": True,
                        "usage_count": 4,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    assert storage.import_json(tmp_path) == [
        {
            "title": "first",
            "content": "body",
            "category": "writing",
            "favorite": False,
            "usage_count": 0,
            "source": "external",
        },
        {
            "title": "second",
            "content": "body",
            "category": "image",
            "favorite": True,
            "usage_count": 4,
        },
    ]


@pytest.mark.parametrize(
    "payload",
    [
        {"prompts": []},
        {"version": 2, "prompts": []},
        {"version": 1},
        {"version": 1, "prompts": [{"title": "missing fields"}]},
    ],
)
def test_import_json_rejects_invalid_payloads_without_mutating_caller_state(
    tmp_path: Path,
    payload: dict,
) -> None:
    original = [{"title": "existing"}]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "prompts.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    with pytest.raises(storage.StorageError):
        storage.import_json(tmp_path)

    assert original == [{"title": "existing"}]


def test_slugify_keeps_korean_ascii_letters_and_numbers() -> None:
    assert storage.slugify(" 한글 Better_TITLE 123!!! ") == "한글-better-title-123"


def test_is_allowed_slug_char_accepts_slug_character_set() -> None:
    assert storage.is_allowed_slug_char("한") is True
    assert storage.is_allowed_slug_char("A") is True
    assert storage.is_allowed_slug_char("7") is True
    assert storage.is_allowed_slug_char("_") is False


def test_json_payload_uses_standard_schema_and_drops_extra_fields() -> None:
    assert storage.json_payload(
        [
            {
                "title": "제목",
                "content": "본문",
                "category": "writing",
                "favorite": True,
                "usage_count": 3,
                "unknown": "kept only in memory",
            }
        ]
    ) == {
        "version": 1,
        "prompts": [
            {
                "title": "제목",
                "content": "본문",
                "category": "writing",
                "favorite": True,
                "usage_count": 3,
            }
        ],
    }


def test_export_markdown_groups_by_category_order_and_prompt_order(
    tmp_path: Path,
) -> None:
    prompts = [
        {
            "title": "First Prompt",
            "content": "본문",
            "category": "Writing",
            "favorite": False,
            "usage_count": 0,
        },
        {
            "title": "Image Prompt",
            "content": "image body",
            "category": "Image",
            "favorite": True,
            "usage_count": 2,
        },
        {
            "title": "Second Prompt",
            "content": "second body",
            "category": "Writing",
            "favorite": False,
            "usage_count": 5,
        },
    ]

    paths = storage.export_markdown(prompts, tmp_path)

    assert paths == [
        tmp_path / "data" / "0001-writing" / "0001-first-prompt.md",
        tmp_path / "data" / "0001-writing" / "0002-second-prompt.md",
        tmp_path / "data" / "0002-image" / "0001-image-prompt.md",
    ]
    assert paths[0].read_text(encoding="utf-8") == (
        "---\n"
        'title: "First Prompt"\n'
        'category: "Writing"\n'
        "favorite: false\n"
        "usage_count: 0\n"
        "---\n\n"
        "본문"
    )


def test_plan_markdown_export_returns_reusable_export_items(tmp_path: Path) -> None:
    prompt = {
        "title": "First Prompt",
        "content": "본문",
        "category": "Writing",
        "favorite": False,
        "usage_count": 0,
    }

    plan = storage.plan_markdown_export([prompt], tmp_path / "data")

    assert plan == [
        storage.MarkdownExportItem(
            directory=tmp_path / "data" / "0001-writing",
            path=tmp_path / "data" / "0001-writing" / "0001-first-prompt.md",
            prompt=prompt,
        )
    ]


def test_group_prompts_by_category_keeps_first_seen_order() -> None:
    writing = {
        "title": "First",
        "content": "body",
        "category": "Writing",
        "favorite": False,
        "usage_count": 0,
    }
    image = {
        "title": "Image",
        "content": "body",
        "category": "Image",
        "favorite": False,
        "usage_count": 0,
    }
    second_writing = {
        "title": "Second",
        "content": "body",
        "category": "Writing",
        "favorite": False,
        "usage_count": 0,
    }

    assert storage.group_prompts_by_category([writing, image, second_writing]) == [
        ("Writing", [writing, second_writing]),
        ("Image", [image]),
    ]


def test_format_markdown_prompt_and_quote_frontmatter_are_public() -> None:
    prompt = {
        "title": '한글 "title"',
        "content": "content",
        "category": "분류",
        "favorite": True,
        "usage_count": 9,
    }

    assert storage.quote_frontmatter(prompt["title"]) == '"한글 \\"title\\""'
    assert storage.format_markdown_prompt(prompt) == (
        "---\n"
        'title: "한글 \\"title\\""\n'
        'category: "분류"\n'
        "favorite: true\n"
        "usage_count: 9\n"
        "---\n\n"
        "content"
    )


def test_export_markdown_escapes_frontmatter_strings_without_escaping_korean(
    tmp_path: Path,
) -> None:
    prompts = [
        {
            "title": '한글 "title" \\ line\nnext',
            "content": "content",
            "category": "분류",
            "favorite": True,
            "usage_count": 9,
        }
    ]

    path = storage.export_markdown(prompts, tmp_path)[0]

    assert path.read_text(encoding="utf-8") == (
        "---\n"
        'title: "한글 \\"title\\" \\\\ line\\nnext"\n'
        'category: "분류"\n'
        "favorite: true\n"
        "usage_count: 9\n"
        "---\n\n"
        "content"
    )


def test_export_markdown_with_zero_prompts_only_ensures_data_directory(
    tmp_path: Path,
) -> None:
    assert storage.export_markdown([], tmp_path) == []
    assert (tmp_path / "data").is_dir()
    assert list((tmp_path / "data").iterdir()) == []


@pytest.mark.parametrize(
    "prompts",
    [
        [
            {
                "title": "valid",
                "content": "body",
                "category": "$$$",
                "favorite": False,
                "usage_count": 0,
            }
        ],
        [
            {
                "title": "!!!",
                "content": "body",
                "category": "valid",
                "favorite": False,
                "usage_count": 0,
            }
        ],
    ],
)
def test_export_markdown_rejects_empty_slugs_without_filesystem_changes(
    tmp_path: Path,
    prompts: list[dict],
) -> None:
    with pytest.raises(storage.StorageError):
        storage.export_markdown(prompts, tmp_path)

    assert not (tmp_path / "data").exists()


def test_export_markdown_rejects_existing_file_at_category_directory(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    blocking_file = data_dir / "0001-writing"
    blocking_file.write_text("not a directory", encoding="utf-8")

    with pytest.raises(storage.StorageError):
        storage.export_markdown(
            [
                {
                    "title": "Prompt",
                    "content": "body",
                    "category": "writing",
                    "favorite": False,
                    "usage_count": 0,
                }
            ],
            tmp_path,
        )

    assert blocking_file.read_text(encoding="utf-8") == "not a directory"


def test_export_markdown_rejects_existing_directory_at_file_path(
    tmp_path: Path,
) -> None:
    file_path_as_dir = tmp_path / "data" / "0001-writing" / "0001-prompt.md"
    file_path_as_dir.mkdir(parents=True)

    with pytest.raises(storage.StorageError):
        storage.export_markdown(
            [
                {
                    "title": "Prompt",
                    "content": "body",
                    "category": "writing",
                    "favorite": False,
                    "usage_count": 0,
                }
            ],
            tmp_path,
        )

    assert file_path_as_dir.is_dir()


def test_export_markdown_rejects_more_than_9999_categories_without_changes(
    tmp_path: Path,
) -> None:
    prompts = [
        {
            "title": f"prompt {index}",
            "content": "body",
            "category": f"category {index}",
            "favorite": False,
            "usage_count": 0,
        }
        for index in range(10000)
    ]

    with pytest.raises(storage.StorageError):
        storage.export_markdown(prompts, tmp_path)

    assert not (tmp_path / "data").exists()


def test_export_markdown_rejects_more_than_9999_prompts_per_category_without_changes(
    tmp_path: Path,
) -> None:
    prompts = [
        {
            "title": f"prompt {index}",
            "content": "body",
            "category": "writing",
            "favorite": False,
            "usage_count": 0,
        }
        for index in range(10000)
    ]

    with pytest.raises(storage.StorageError):
        storage.export_markdown(prompts, tmp_path)

    assert not (tmp_path / "data").exists()
