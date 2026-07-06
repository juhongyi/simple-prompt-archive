import archive
from console_handlers import (
    handle_add_prompt,
    handle_category_view,
    handle_delete,
    handle_detail_view,
    handle_favorite_toggle,
    handle_favorites,
    handle_json_export,
    handle_json_import,
    handle_list_prompts,
    handle_markdown_export,
    handle_search,
    handle_update,
    handle_usage_sorted,
)
from console_io import (
    read_line,
    read_multiline_content,
    read_number,
    read_prompt_selection,
    read_required_text,
)
from console_views import (
    favorite_marker,
    print_prompt_rows,
    print_search_rows,
    show_prompt_detail,
    show_prompt_list_detail_flow,
)
from prompt_schema import EDIT_FIELD_CHOICES


MENU_ITEMS = (
    ("1", "프롬프트 추가"),
    ("2", "목록 보기"),
    ("3", "카테고리별 조회"),
    ("4", "검색"),
    ("5", "상세 보기"),
    ("6", "즐겨찾기 관리"),
    ("7", "즐겨찾기 목록"),
    ("8", "수정"),
    ("9", "삭제"),
    ("10", "조회수 정렬 목록"),
    ("11", "JSON 내보내기"),
    ("12", "JSON 가져오기"),
    ("13", "Markdown 내보내기"),
    ("0", "종료"),
)


def run_app(input_func=input, output_func=print, root=None, prompts=None):
    active_prompts = prompts if prompts is not None else archive.create_starter_prompts()

    while True:
        print_menu(output_func)
        try:
            choice = read_line(input_func).strip()
        except EOFError:
            output_func("입력이 종료되어 프로그램을 종료합니다.")
            break

        if choice == "0":
            output_func("프로그램을 종료합니다.")
            break
        try:
            action = MENU_ACTIONS.get(choice)
            if action is None:
                output_func("올바른 메뉴 번호를 입력해주세요.")
            else:
                action(active_prompts, input_func, output_func, root)
        except EOFError:
            output_func("입력이 종료되어 프로그램을 종료합니다.")
            break

    return active_prompts


def print_menu(output_func):
    output_func("")
    output_func("Simple Prompt Archive")
    for number, label in MENU_ITEMS:
        output_func(f"{number}. {label}")
    output_func("메뉴 번호를 입력하세요:")


MENU_ACTIONS = {
    "1": lambda prompts, input_func, output_func, root: handle_add_prompt(
        prompts,
        input_func,
        output_func,
    ),
    "2": lambda prompts, input_func, output_func, root: handle_list_prompts(
        prompts,
        input_func,
        output_func,
    ),
    "3": lambda prompts, input_func, output_func, root: handle_category_view(
        prompts,
        input_func,
        output_func,
    ),
    "4": lambda prompts, input_func, output_func, root: handle_search(
        prompts,
        input_func,
        output_func,
    ),
    "5": lambda prompts, input_func, output_func, root: handle_detail_view(
        prompts,
        input_func,
        output_func,
    ),
    "6": lambda prompts, input_func, output_func, root: handle_favorite_toggle(
        prompts,
        input_func,
        output_func,
    ),
    "7": lambda prompts, input_func, output_func, root: handle_favorites(
        prompts,
        input_func,
        output_func,
    ),
    "8": lambda prompts, input_func, output_func, root: handle_update(
        prompts,
        input_func,
        output_func,
    ),
    "9": lambda prompts, input_func, output_func, root: handle_delete(
        prompts,
        input_func,
        output_func,
    ),
    "10": lambda prompts, input_func, output_func, root: handle_usage_sorted(
        prompts,
        input_func,
        output_func,
    ),
    "11": lambda prompts, input_func, output_func, root: handle_json_export(
        prompts,
        output_func,
        root,
    ),
    "12": lambda prompts, input_func, output_func, root: handle_json_import(
        prompts,
        output_func,
        root,
    ),
    "13": lambda prompts, input_func, output_func, root: handle_markdown_export(
        prompts,
        output_func,
        root,
    ),
}
