import archive
import pytest


def test_starter_prompts_include_required_fields() -> None:
    prompts = archive.create_starter_prompts()

    assert len(prompts) >= 3
    for prompt in prompts:
        assert set(archive.STANDARD_FIELDS).issubset(prompt)
        assert isinstance(prompt["favorite"], bool)
        assert isinstance(prompt["usage_count"], int)


def test_add_prompt_trims_required_values_and_appends_in_order() -> None:
    prompts = []

    prompt = archive.add_prompt(
        prompts,
        "  제목  ",
        "  본문\n",
        "  writing  ",
    )

    assert prompts == [
        {
            "title": "제목",
            "content": "본문",
            "category": "writing",
            "favorite": False,
            "usage_count": 0,
        }
    ]
    assert prompt is prompts[-1]


@pytest.mark.parametrize(
    ("title", "content", "category"),
    [
        ("", "본문", "분류"),
        ("제목", "   ", "분류"),
        ("제목", "본문", "\t"),
    ],
)
def test_add_prompt_rejects_blank_required_values(
    title: str,
    content: str,
    category: str,
) -> None:
    prompts = []

    with pytest.raises(ValueError, match="필수 입력 항목"):
        archive.add_prompt(prompts, title, content, category)

    assert prompts == []


def test_categories_keep_first_seen_registration_order() -> None:
    prompts = [
        {"category": "writing"},
        {"category": "image"},
        {"category": "writing"},
        {"category": "automation"},
    ]

    assert archive.list_categories(prompts) == ["writing", "image", "automation"]


def test_filter_by_category_keeps_registration_order() -> None:
    first = {"title": "first", "category": "writing"}
    second = {"title": "second", "category": "image"}
    third = {"title": "third", "category": "writing"}

    assert archive.filter_by_category([first, second, third], "writing") == [
        first,
        third,
    ]


def test_search_matches_title_and_content_case_insensitively_for_english() -> None:
    prompts = [
        {"title": "Marketing Plan", "content": "outline", "category": "writing"},
        {"title": "Image", "content": "Create a LOGO concept", "category": "image"},
        {"title": "Automation", "content": "daily summary", "category": "work"},
    ]

    assert archive.search_prompts(prompts, "plan") == [prompts[0]]
    assert archive.search_prompts(prompts, "logo") == [prompts[1]]


def test_record_detail_view_increments_usage_count() -> None:
    prompt = {"title": "Prompt", "usage_count": 2}

    archive.record_detail_view(prompt)

    assert prompt["usage_count"] == 3


def test_toggle_favorite_flips_state() -> None:
    prompt = {"title": "Prompt", "favorite": False}

    assert archive.toggle_favorite(prompt) is True
    assert archive.toggle_favorite(prompt) is False


def test_favorite_prompts_keep_registration_order() -> None:
    prompts = [
        {"title": "first", "favorite": True},
        {"title": "second", "favorite": False},
        {"title": "third", "favorite": True},
    ]

    assert archive.favorite_prompts(prompts) == [prompts[0], prompts[2]]


def test_update_prompt_field_trims_text_without_touching_other_state() -> None:
    prompt = {
        "title": "old",
        "content": "body",
        "category": "writing",
        "favorite": True,
        "usage_count": 7,
    }

    archive.update_prompt_field(prompt, "title", "  new  ")

    assert prompt == {
        "title": "new",
        "content": "body",
        "category": "writing",
        "favorite": True,
        "usage_count": 7,
    }


def test_update_prompt_field_rejects_blank_and_unsupported_fields() -> None:
    prompt = {"title": "old", "content": "body", "category": "writing"}

    with pytest.raises(ValueError, match="필수 입력 항목"):
        archive.update_prompt_field(prompt, "content", "  ")

    with pytest.raises(ValueError, match="수정할 수 없는 필드"):
        archive.update_prompt_field(prompt, "favorite", "true")

    assert prompt == {"title": "old", "content": "body", "category": "writing"}


def test_delete_prompt_by_number_removes_selected_prompt() -> None:
    prompts = [{"title": "first"}, {"title": "second"}, {"title": "third"}]

    deleted = archive.delete_prompt_by_number(prompts, 2)

    assert deleted == {"title": "second"}
    assert prompts == [{"title": "first"}, {"title": "third"}]


@pytest.mark.parametrize("number", [0, 4])
def test_delete_prompt_by_number_rejects_out_of_range_number(number: int) -> None:
    prompts = [{"title": "first"}, {"title": "second"}, {"title": "third"}]

    with pytest.raises(IndexError):
        archive.delete_prompt_by_number(prompts, number)

    assert prompts == [{"title": "first"}, {"title": "second"}, {"title": "third"}]


def test_sort_by_usage_count_descending_preserves_registration_order_for_ties() -> None:
    prompts = [
        {"title": "first", "usage_count": 2},
        {"title": "second", "usage_count": 5},
        {"title": "third", "usage_count": 5},
        {"title": "fourth", "usage_count": 1},
    ]

    assert archive.sort_by_usage_count(prompts) == [
        prompts[1],
        prompts[2],
        prompts[0],
        prompts[3],
    ]


def test_select_prompt_by_number_returns_none_for_cancel() -> None:
    prompts = [{"title": "first"}, {"title": "second"}]

    assert archive.select_prompt_by_number(prompts, 0) is None
    assert archive.select_prompt_by_number(prompts, 2) == {"title": "second"}


@pytest.mark.parametrize("number", [-1, 3])
def test_select_prompt_by_number_rejects_out_of_range(number: int) -> None:
    prompts = [{"title": "first"}, {"title": "second"}]

    with pytest.raises(IndexError):
        archive.select_prompt_by_number(prompts, number)
