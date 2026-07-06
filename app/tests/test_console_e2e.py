import json
from collections.abc import Callable
from pathlib import Path

import archive
import console


def test_user_adds_reuses_exports_and_deletes_prompt(tmp_path: Path) -> None:
    prompts, outputs = run_app_with_inputs(tmp_path, core_user_journey_inputs())

    exported_prompt = find_prompt(
        read_exported_prompts(tmp_path), "Weekly Review Coach"
    )

    assert prompts == archive.create_starter_prompts()
    assert exported_prompt["category"] == "work"
    assert exported_prompt["favorite"] is True
    assert exported_prompt["usage_count"] == 3
    assert exported_prompt["content"] == "Summarize blockers\nSuggest next actions"
    assert markdown_prompt_path(tmp_path, "work", "weekly-review-coach").is_file()
    assert count_output(outputs, "프롬프트 상세") == 3


def test_user_recovers_from_common_input_mistakes(tmp_path: Path) -> None:
    prompts, outputs = run_app_with_inputs(tmp_path, input_recovery_journey_inputs())

    added_prompt = find_prompt(prompts, "Retry Prompt")

    assert added_prompt["category"] == "recovery"
    assert added_prompt["usage_count"] == 0
    assert count_output(outputs, "올바른 메뉴 번호를 입력해주세요.") == 1
    assert count_output(outputs, "필수 입력 항목은 비워둘 수 없습니다.") == 1
    assert count_output(outputs, "목록 번호가 범위를 벗어났습니다.") == 1
    assert count_output(outputs, "메뉴로 돌아갑니다.") == 1


def core_user_journey_inputs() -> list[str]:
    return [
        *add_prompt_inputs(
            "Weekly review",
            ["Summarize blockers", "Suggest next actions"],
            "work",
        ),
        *open_prompt_from_full_list_inputs("4"),
        *toggle_favorite_inputs("4"),
        *open_prompt_from_favorites_inputs("1"),
        *rename_prompt_inputs("4", "Weekly Review Coach"),
        *search_inputs("weekly"),
        *open_prompt_from_usage_sorted_inputs("1"),
        *export_json_inputs(),
        *export_markdown_inputs(),
        *delete_prompt_inputs("4"),
        *exit_inputs(),
    ]


def input_recovery_journey_inputs() -> list[str]:
    return [
        "invalid",
        *add_prompt_with_blank_title_retry_inputs(
            "Retry Prompt",
            ["body"],
            "recovery",
        ),
        *open_detail_with_invalid_selection_inputs("99"),
        *cancel_full_list_inputs(),
        *exit_inputs(),
    ]


def add_prompt_inputs(title: str, content_lines: list[str], category: str) -> list[str]:
    return ["1", title, *content_lines, "EOF", category]


def add_prompt_with_blank_title_retry_inputs(
    title: str,
    content_lines: list[str],
    category: str,
) -> list[str]:
    return ["1", " ", title, *content_lines, "EOF", category]


def open_prompt_from_full_list_inputs(prompt_number: str) -> list[str]:
    return ["2", prompt_number]


def toggle_favorite_inputs(prompt_number: str) -> list[str]:
    return ["6", prompt_number]


def open_prompt_from_favorites_inputs(prompt_number: str) -> list[str]:
    return ["7", prompt_number]


def rename_prompt_inputs(prompt_number: str, title: str) -> list[str]:
    return ["8", prompt_number, "1", title]


def search_inputs(keyword: str) -> list[str]:
    return ["4", keyword]


def open_prompt_from_usage_sorted_inputs(prompt_number: str) -> list[str]:
    return ["10", prompt_number]


def export_json_inputs() -> list[str]:
    return ["11"]


def export_markdown_inputs() -> list[str]:
    return ["13"]


def delete_prompt_inputs(prompt_number: str) -> list[str]:
    return ["9", prompt_number]


def open_detail_with_invalid_selection_inputs(prompt_number: str) -> list[str]:
    return ["5", prompt_number]


def cancel_full_list_inputs() -> list[str]:
    return ["2", "0"]


def exit_inputs() -> list[str]:
    return ["0"]


def run_app_with_inputs(
    root: Path,
    inputs: list[str],
) -> tuple[list[dict], list[str]]:
    outputs: list[str] = []
    prompts = console.run_app(
        make_scripted_input(inputs),
        collect_output(outputs),
        root=root,
    )
    return prompts, outputs


def make_scripted_input(inputs: list[str]) -> Callable[[], str]:
    remaining_inputs = list(inputs)

    def input_func() -> str:
        if not remaining_inputs:
            raise EOFError
        return remaining_inputs.pop(0)

    return input_func


def collect_output(outputs: list[str]) -> Callable[[str], None]:
    def output_func(message: str = "") -> None:
        outputs.append(str(message))

    return output_func


def read_exported_prompts(root: Path) -> list[dict]:
    payload = json.loads((root / "data" / "prompts.json").read_text(encoding="utf-8"))
    return payload["prompts"]


def find_prompt(prompts: list[dict], title: str) -> dict:
    for prompt in prompts:
        if prompt["title"] == title:
            return prompt
    raise AssertionError(f"Prompt not found: {title}")


def markdown_prompt_path(root: Path, category_slug: str, prompt_slug: str) -> Path:
    return root / "data" / f"0004-{category_slug}" / f"0001-{prompt_slug}.md"


def count_output(outputs: list[str], message: str) -> int:
    return outputs.count(message)
