from prompt_archive.prompts import (
    add_prompt,
    delete_prompt,
    edit_prompt_field,
    favorite_prompts,
    filter_by_category,
    get_categories,
    search_prompts,
    starter_prompts,
    toggle_favorite,
    usage_sorted_prompts,
    view_prompt,
)


def test_starter_prompts_cover_repeated_ai_use_cases() -> None:
    prompts = starter_prompts()

    assert len(prompts) >= 3
    assert {prompt["favorite"] for prompt in prompts} == {False}
    assert {prompt["usage_count"] for prompt in prompts} == {0}
    assert all(prompt["title"] for prompt in prompts)
    assert all(prompt["content"] for prompt in prompts)
    assert all(prompt["category"] for prompt in prompts)


def test_add_prompt_appends_with_default_state() -> None:
    prompts = []

    added = add_prompt(prompts, "Blog outline", "Write an outline", "Writing")

    assert prompts == [
        {
            "title": "Blog outline",
            "content": "Write an outline",
            "category": "Writing",
            "favorite": False,
            "usage_count": 0,
        }
    ]
    assert added is prompts[-1]


def test_add_prompt_allows_duplicate_title_and_content() -> None:
    prompts = []

    add_prompt(prompts, "Repeat", "Same body", "Writing")
    add_prompt(prompts, "Repeat", "Same body", "Writing")

    assert len(prompts) == 2
    assert prompts[0] is not prompts[1]
    assert prompts[0] == prompts[1]


def test_add_prompt_rejects_blank_required_fields() -> None:
    prompts = []

    for title, content, category in [
        ("", "Body", "Writing"),
        ("Title", "", "Writing"),
        ("Title", "Body", ""),
        ("   ", "Body", "Writing"),
    ]:
        try:
            add_prompt(prompts, title, content, category)
        except ValueError:
            pass
        else:
            raise AssertionError("blank field should be rejected")

    assert prompts == []


def test_categories_keep_first_registration_order() -> None:
    prompts = [
        {"title": "A", "content": "A", "category": "Writing", "favorite": False, "usage_count": 0},
        {"title": "B", "content": "B", "category": "Images", "favorite": False, "usage_count": 0},
        {"title": "C", "content": "C", "category": "Writing", "favorite": False, "usage_count": 0},
    ]

    assert get_categories(prompts) == ["Writing", "Images"]
    assert [prompt["title"] for prompt in filter_by_category(prompts, "Writing")] == ["A", "C"]


def test_search_matches_title_and_content_case_insensitively_for_english() -> None:
    prompts = [
        {"title": "Better Title", "content": "Improve the heading", "category": "Writing", "favorite": False, "usage_count": 0},
        {"title": "Storyboard", "content": "Create IMAGE prompts", "category": "Images", "favorite": False, "usage_count": 0},
        {"title": "Automation", "content": "Schedule tasks", "category": "Workflow", "favorite": False, "usage_count": 0},
    ]

    assert [prompt["title"] for prompt in search_prompts(prompts, "title")] == ["Better Title"]
    assert [prompt["title"] for prompt in search_prompts(prompts, "image")] == ["Storyboard"]
    assert search_prompts(prompts, "missing") == []


def test_view_prompt_increments_usage_count() -> None:
    prompt = {"title": "A", "content": "A", "category": "Writing", "favorite": False, "usage_count": 2}

    viewed = view_prompt(prompt)

    assert viewed is prompt
    assert prompt["usage_count"] == 3


def test_favorite_toggle_and_listing_keep_registration_order() -> None:
    prompts = [
        {"title": "A", "content": "A", "category": "Writing", "favorite": False, "usage_count": 0},
        {"title": "B", "content": "B", "category": "Images", "favorite": True, "usage_count": 0},
        {"title": "C", "content": "C", "category": "Workflow", "favorite": False, "usage_count": 0},
    ]

    toggle_favorite(prompts[0])
    toggle_favorite(prompts[2])

    assert [prompt["title"] for prompt in favorite_prompts(prompts)] == ["A", "B", "C"]
    toggle_favorite(prompts[1])
    assert [prompt["title"] for prompt in favorite_prompts(prompts)] == ["A", "C"]


def test_edit_prompt_field_changes_only_allowed_fields() -> None:
    prompt = {"title": "A", "content": "A", "category": "Writing", "favorite": True, "usage_count": 5}

    edit_prompt_field(prompt, "title", "New title")
    edit_prompt_field(prompt, "content", "New body")
    edit_prompt_field(prompt, "category", "New category")

    assert prompt == {
        "title": "New title",
        "content": "New body",
        "category": "New category",
        "favorite": True,
        "usage_count": 5,
    }


def test_edit_prompt_field_rejects_invalid_or_blank_values() -> None:
    prompt = {"title": "A", "content": "A", "category": "Writing", "favorite": False, "usage_count": 0}

    for field, value in [("favorite", "yes"), ("usage_count", "4"), ("title", "  ")]:
        try:
            edit_prompt_field(prompt, field, value)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid edit should be rejected")

    assert prompt == {"title": "A", "content": "A", "category": "Writing", "favorite": False, "usage_count": 0}


def test_delete_prompt_removes_selected_item() -> None:
    prompts = [
        {"title": "A", "content": "A", "category": "Writing", "favorite": False, "usage_count": 0},
        {"title": "B", "content": "B", "category": "Images", "favorite": False, "usage_count": 0},
    ]

    deleted = delete_prompt(prompts, 0)

    assert deleted["title"] == "A"
    assert [prompt["title"] for prompt in prompts] == ["B"]


def test_usage_sorted_prompts_orders_by_count_and_preserves_ties() -> None:
    prompts = [
        {"title": "A", "content": "A", "category": "Writing", "favorite": False, "usage_count": 2},
        {"title": "B", "content": "B", "category": "Images", "favorite": False, "usage_count": 5},
        {"title": "C", "content": "C", "category": "Workflow", "favorite": False, "usage_count": 5},
        {"title": "D", "content": "D", "category": "Writing", "favorite": False, "usage_count": 1},
    ]

    assert [prompt["title"] for prompt in usage_sorted_prompts(prompts)] == ["B", "C", "A", "D"]
