from pathlib import Path

from prompt_archive.console import run_app


def run_with_inputs(inputs: list[str], prompts: list[dict[str, object]] | None = None, data_dir: Path | None = None):
    remaining = list(inputs)
    output: list[str] = []

    def input_func(prompt: str = "") -> str:
        output.append(prompt)
        if not remaining:
            raise AssertionError("no more test input")
        return remaining.pop(0)

    kwargs = {"prompts": prompts, "input_func": input_func, "output_func": output.append}
    if data_dir is not None:
        kwargs["data_dir"] = data_dir
    run_app(**kwargs)
    return output


def make_prompts() -> list[dict[str, object]]:
    return [
        {
            "title": "First",
            "content": "First body",
            "category": "Writing",
            "favorite": False,
            "usage_count": 0,
        },
        {
            "title": "Second",
            "content": "Second body",
            "category": "Images",
            "favorite": True,
            "usage_count": 2,
        },
    ]


def test_menu_starts_with_starter_prompts_and_exits() -> None:
    output = run_with_inputs(["2", "0", "14"])

    assert any("Simple Prompt Archive" in line for line in output)
    assert any("Sharper writing assistant" in line for line in output)
    assert any("Image concept generator" in line for line in output)
    assert any("Goodbye." in line for line in output)


def test_invalid_menu_input_keeps_flow() -> None:
    output = run_with_inputs(["abc", "99", "14"], prompts=make_prompts())

    assert output.count("Invalid choice. Please enter a listed number.") == 2
    assert any("Goodbye." in line for line in output)


def test_add_prompt_retries_blank_required_fields() -> None:
    prompts = make_prompts()

    output = run_with_inputs(
        ["1", "", "New title", "New body", "New category", "14"],
        prompts=prompts,
    )

    assert prompts[-1]["title"] == "New title"
    assert prompts[-1]["favorite"] is False
    assert prompts[-1]["usage_count"] == 0
    assert "Title is required." in output
    assert "Prompt added." in output


def test_list_prompt_selection_views_detail_and_zero_returns_to_menu() -> None:
    prompts = make_prompts()

    output = run_with_inputs(["2", "2", "2", "0", "14"], prompts=prompts)

    assert prompts[1]["usage_count"] == 3
    assert prompts[0]["usage_count"] == 0
    assert any("Title: Second" in line for line in output)
    assert any("Returning to main menu." in line for line in output)


def test_category_flow_uses_category_and_prompt_screen_numbering() -> None:
    prompts = make_prompts()

    output = run_with_inputs(["3", "2", "1", "14"], prompts=prompts)

    assert prompts[1]["usage_count"] == 3
    assert any("1. Writing" in line for line in output)
    assert any("2. Images" in line for line in output)
    assert any("Title: Second" in line for line in output)


def test_search_results_do_not_prompt_for_detail_selection() -> None:
    prompts = make_prompts()

    output = run_with_inputs(["4", "second", "14"], prompts=prompts)

    assert prompts[1]["usage_count"] == 2
    assert any("Second" in line for line in output)
    assert not any("Select a prompt number" in line for line in output)


def test_favorite_toggle_and_favorite_list_detail_flow() -> None:
    prompts = make_prompts()

    output = run_with_inputs(["6", "1", "7", "1", "14"], prompts=prompts)

    assert prompts[0]["favorite"] is True
    assert prompts[0]["usage_count"] == 1
    assert any("Favorite is now on." in line for line in output)
    assert any("Title: First" in line for line in output)


def test_edit_and_delete_flows_update_selected_prompt() -> None:
    prompts = make_prompts()

    output = run_with_inputs(["8", "1", "1", "", "Renamed", "9", "2", "14"], prompts=prompts)

    assert [prompt["title"] for prompt in prompts] == ["Renamed"]
    assert "New value is required." in output
    assert "Prompt updated." in output
    assert "Prompt deleted." in output


def test_usage_sorted_flow_selects_from_sorted_numbering() -> None:
    prompts = make_prompts()

    output = run_with_inputs(["10", "1", "14"], prompts=prompts)

    assert prompts[1]["usage_count"] == 3
    assert any("1. [Images] Second * (views: 2)" in line for line in output)
    assert any("Title: Second" in line for line in output)


def test_json_export_import_and_markdown_export_menu_items(tmp_path) -> None:
    prompts = make_prompts()
    data_dir = tmp_path / "data"

    export_output = run_with_inputs(["11", "14"], prompts=prompts, data_dir=data_dir)
    prompts[0]["title"] = "Changed"
    import_output = run_with_inputs(["12", "13", "14"], prompts=prompts, data_dir=data_dir)

    assert prompts[0]["title"] == "First"
    assert (data_dir / "prompts.json").is_file()
    assert (data_dir / "0001-writing" / "0001-first.md").is_file()
    assert "JSON exported." in export_output
    assert "JSON imported." in import_output
    assert "Markdown exported." in import_output
