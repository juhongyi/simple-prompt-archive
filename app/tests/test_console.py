import json
from pathlib import Path

import console


class ScriptedIO:
    def __init__(self, inputs: list[str]) -> None:
        self.inputs = inputs
        self.outputs: list[str] = []

    def input(self) -> str:
        if not self.inputs:
            raise EOFError
        return self.inputs.pop(0)

    def output(self, message: str = "") -> None:
        self.outputs.append(str(message))

    def text(self) -> str:
        return "\n".join(self.outputs)


def test_read_required_text_retries_blank_and_trims_value() -> None:
    io = ScriptedIO(["  ", "  제목  "])

    assert console.read_required_text("제목", io.input, io.output) == "제목"
    assert "비워둘 수 없습니다" in io.text()


def test_read_multiline_content_uses_eof_sentinel_and_trims_content() -> None:
    io = ScriptedIO(["  line one", "line two  ", "EOF"])

    assert console.read_multiline_content(io.input, io.output) == "line one\nline two"


def test_handle_add_prompt_adds_trimmed_prompt_with_multiline_content() -> None:
    prompts = []
    io = ScriptedIO(["  Title  ", "line one", "line two", "EOF", "  writing  "])

    console.handle_add_prompt(prompts, io.input, io.output)

    assert prompts == [
        {
            "title": "Title",
            "content": "line one\nline two",
            "category": "writing",
            "favorite": False,
            "usage_count": 0,
        }
    ]


def test_handle_list_prompts_cancel_does_not_increment_usage() -> None:
    prompts = [_prompt("First", usage_count=0)]
    io = ScriptedIO(["0"])

    console.handle_list_prompts(prompts, io.input, io.output)

    assert prompts[0]["usage_count"] == 0


def test_handle_list_prompts_selects_current_display_number_for_detail() -> None:
    prompts = [_prompt("First", usage_count=0), _prompt("Second", usage_count=5)]
    io = ScriptedIO(["2"])

    console.handle_list_prompts(prompts, io.input, io.output)

    assert prompts[0]["usage_count"] == 0
    assert prompts[1]["usage_count"] == 6
    assert "제목: Second" in io.text()


def test_handle_category_view_uses_category_order_and_category_prompt_number() -> None:
    prompts = [
        _prompt("Writing first", category="writing", usage_count=0),
        _prompt("Image", category="image", usage_count=0),
        _prompt("Writing second", category="writing", usage_count=0),
    ]
    io = ScriptedIO(["1", "2"])

    console.handle_category_view(prompts, io.input, io.output)

    assert prompts[0]["usage_count"] == 0
    assert prompts[1]["usage_count"] == 0
    assert prompts[2]["usage_count"] == 1
    assert "Writing second" in io.text()


def test_handle_search_displays_results_without_detail_selection() -> None:
    prompts = [
        _prompt("Marketing Plan", content="outline", usage_count=0),
        _prompt("Image", content="Create a LOGO concept", usage_count=0),
    ]
    io = ScriptedIO(["logo"])

    console.handle_search(prompts, io.input, io.output)

    assert prompts[0]["usage_count"] == 0
    assert prompts[1]["usage_count"] == 0
    assert "Image" in io.text()


def test_handle_detail_view_rejects_invalid_number_without_mutation() -> None:
    prompts = [_prompt("First", usage_count=0)]
    io = ScriptedIO(["2"])

    console.handle_detail_view(prompts, io.input, io.output)

    assert prompts[0]["usage_count"] == 0
    assert "범위를 벗어났습니다" in io.text()


def test_handle_favorite_toggle_and_favorite_list_detail_flow() -> None:
    prompts = [_prompt("First", usage_count=0), _prompt("Second", usage_count=0)]
    toggle_io = ScriptedIO(["2"])
    list_io = ScriptedIO(["1"])

    console.handle_favorite_toggle(prompts, toggle_io.input, toggle_io.output)
    console.handle_favorites(prompts, list_io.input, list_io.output)

    assert prompts[0]["favorite"] is False
    assert prompts[1]["favorite"] is True
    assert prompts[1]["usage_count"] == 1
    assert "즐겨찾기 설정" in toggle_io.text()


def test_handle_update_changes_selected_field_without_touching_state() -> None:
    prompts = [_prompt("First", favorite=True, usage_count=3)]
    io = ScriptedIO(["1", "1", "  Updated  "])

    console.handle_update(prompts, io.input, io.output)

    assert prompts[0]["title"] == "Updated"
    assert prompts[0]["favorite"] is True
    assert prompts[0]["usage_count"] == 3


def test_handle_delete_removes_selected_prompt() -> None:
    prompts = [_prompt("First"), _prompt("Second")]
    io = ScriptedIO(["1"])

    console.handle_delete(prompts, io.input, io.output)

    assert [prompt["title"] for prompt in prompts] == ["Second"]


def test_handle_usage_sorted_selects_number_from_sorted_display() -> None:
    prompts = [_prompt("First", usage_count=1), _prompt("Second", usage_count=5)]
    io = ScriptedIO(["1"])

    console.handle_usage_sorted(prompts, io.input, io.output)

    assert prompts[0]["usage_count"] == 1
    assert prompts[1]["usage_count"] == 6
    assert "Second" in io.text()


def test_json_import_handler_replaces_prompts_only_on_success(tmp_path: Path) -> None:
    prompts = [_prompt("Existing")]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "prompts.json").write_text(
        json.dumps(
            {
                "version": 1,
                "prompts": [
                    {
                        "title": "Imported",
                        "content": "body",
                        "category": "writing",
                        "favorite": False,
                        "usage_count": 0,
                        "extra": "preserved",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    io = ScriptedIO([])

    console.handle_json_import(prompts, io.output, tmp_path)

    assert prompts == [
        {
            "title": "Imported",
            "content": "body",
            "category": "writing",
            "favorite": False,
            "usage_count": 0,
            "extra": "preserved",
        }
    ]
    assert "가져오기 완료" in io.text()


def test_json_import_handler_keeps_prompts_on_failure(tmp_path: Path) -> None:
    prompts = [_prompt("Existing")]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "prompts.json").write_text(
        json.dumps({"version": 2, "prompts": []}),
        encoding="utf-8",
    )
    io = ScriptedIO([])

    console.handle_json_import(prompts, io.output, tmp_path)

    assert prompts == [_prompt("Existing")]
    assert "가져오기 실패" in io.text()


def test_markdown_export_handler_reports_written_count(tmp_path: Path) -> None:
    prompts = [_prompt("Prompt")]
    io = ScriptedIO([])

    console.handle_markdown_export(prompts, io.output, tmp_path)

    assert "1개" in io.text()
    assert (tmp_path / "data" / "0001-writing" / "0001-prompt.md").is_file()


def test_run_app_handles_invalid_menu_choices_and_exit() -> None:
    io = ScriptedIO(["abc", "99", "0"])

    console.run_app(io.input, io.output)

    assert io.text().count("올바른 메뉴 번호를 입력해주세요.") == 2
    assert "프로그램을 종료합니다." in io.text()


def test_run_app_handles_eof_inside_menu_action() -> None:
    io = ScriptedIO(["1", "Title"])

    console.run_app(io.input, io.output, prompts=[])

    assert "입력이 종료되어 프로그램을 종료합니다." in io.text()


def _prompt(
    title: str,
    content: str = "body",
    category: str = "writing",
    favorite: bool = False,
    usage_count: int = 0,
) -> dict:
    return {
        "title": title,
        "content": content,
        "category": category,
        "favorite": favorite,
        "usage_count": usage_count,
    }
