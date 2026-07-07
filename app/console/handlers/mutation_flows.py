import archive

from ..constants import EDIT_FIELD_CHOICES
from ..io import (
    read_multiline_content,
    read_number,
    read_prompt_selection,
    read_required_text,
)
from ..views import print_prompt_rows
from .prompt_flows import show_prompt_list_detail_flow


def handle_favorite_toggle(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    output_func("즐겨찾기 관리")
    print_prompt_rows(prompts, output_func, include_category=True)
    selected = read_prompt_selection(prompts, input_func, output_func)
    if selected is None:
        return

    enabled = archive.toggle_favorite(selected)
    state = "설정" if enabled else "해제"
    output_func(f"즐겨찾기 {state}: {selected['title']}")


def handle_favorites(prompts, input_func, output_func):
    favorites = archive.favorite_prompts(prompts)
    show_prompt_list_detail_flow(
        favorites,
        input_func,
        output_func,
        "즐겨찾기 목록",
        include_category=True,
        empty_message="즐겨찾기된 프롬프트가 없습니다.",
    )


def handle_update(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    output_func("수정할 프롬프트 목록")
    print_prompt_rows(prompts, output_func, include_category=True)
    selected = read_prompt_selection(prompts, input_func, output_func)
    if selected is None:
        return

    output_func("수정할 필드를 선택하세요.")
    for number, (_, label) in EDIT_FIELD_CHOICES.items():
        output_func(f"{number}. {label}")
    output_func("0. 메뉴로 돌아가기")

    try:
        field_number = read_number(input_func)
    except ValueError:
        output_func("숫자를 입력해주세요.")
        return

    if field_number == 0:
        output_func("메뉴로 돌아갑니다.")
        return
    if field_number not in EDIT_FIELD_CHOICES:
        output_func("올바른 수정 필드 번호를 입력해주세요.")
        return

    field_name, label = EDIT_FIELD_CHOICES[field_number]
    if field_name == "content":
        value = read_multiline_content(input_func, output_func)
    else:
        value = read_required_text(label, input_func, output_func)
    archive.update_prompt_field(selected, field_name, value)
    output_func("프롬프트를 수정했습니다.")


def handle_delete(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    output_func("삭제할 프롬프트 목록")
    print_prompt_rows(prompts, output_func, include_category=True)
    output_func("프롬프트 번호를 입력하세요. 0은 메뉴로 돌아갑니다:")

    try:
        number = read_number(input_func)
        if number == 0:
            output_func("메뉴로 돌아갑니다.")
            return
        deleted = archive.delete_prompt_by_number(prompts, number)
    except ValueError:
        output_func("숫자를 입력해주세요.")
        return
    except IndexError as exc:
        output_func(str(exc))
        return

    output_func(f"프롬프트를 삭제했습니다: {deleted['title']}")
