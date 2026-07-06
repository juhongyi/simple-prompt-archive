import archive
import storage

from .constants import EDIT_FIELD_CHOICES
from .io import (
    read_multiline_content,
    read_number,
    read_prompt_selection,
    read_required_text,
)
from .views import print_prompt_rows, print_search_rows, show_prompt_detail


def handle_add_prompt(prompts, input_func, output_func):
    title = read_required_text("제목", input_func, output_func)
    content = read_multiline_content(input_func, output_func)
    category = read_required_text("카테고리", input_func, output_func)
    archive.add_prompt(prompts, title, content, category)
    output_func("프롬프트를 추가했습니다.")


def handle_list_prompts(prompts, input_func, output_func):
    show_prompt_list_detail_flow(
        prompts,
        input_func,
        output_func,
        "전체 프롬프트 목록",
        include_category=True,
    )


def handle_category_view(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    categories = archive.list_categories(prompts)
    output_func("카테고리 목록")
    for index, category in enumerate(categories, start=1):
        output_func(f"{index}. {category}")
    output_func("카테고리 번호를 입력하세요. 0은 메뉴로 돌아갑니다:")

    try:
        number = read_number(input_func)
        if number == 0:
            output_func("메뉴로 돌아갑니다.")
            return
        if number < 1 or number > len(categories):
            raise IndexError("목록 번호가 범위를 벗어났습니다.")
    except ValueError:
        output_func("숫자를 입력해주세요.")
        return
    except IndexError as exc:
        output_func(str(exc))
        return

    category_prompts = archive.filter_by_category(prompts, categories[number - 1])
    if not category_prompts:
        output_func("결과가 없습니다.")
        return

    show_prompt_list_detail_flow(
        category_prompts,
        input_func,
        output_func,
        f"{categories[number - 1]} 프롬프트 목록",
        include_category=False,
    )


def handle_search(prompts, input_func, output_func):
    keyword = read_required_text("검색어", input_func, output_func)
    results = archive.search_prompts(prompts, keyword)
    if not results:
        output_func("검색 결과가 없습니다.")
        return

    output_func("검색 결과")
    print_search_rows(results, output_func)


def handle_detail_view(prompts, input_func, output_func):
    show_prompt_list_detail_flow(
        prompts,
        input_func,
        output_func,
        "상세 보기 프롬프트 목록",
        include_category=True,
    )


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


def handle_usage_sorted(prompts, input_func, output_func):
    sorted_prompts = archive.sort_by_usage_count(prompts)
    show_prompt_list_detail_flow(
        sorted_prompts,
        input_func,
        output_func,
        "조회수 정렬 목록",
        include_category=True,
        include_usage=True,
    )


def handle_json_export(prompts, output_func, root=None):
    try:
        path = storage.export_json(prompts, root)
    except Exception as exc:
        output_func(f"JSON 내보내기 실패: {exc}")
        return
    output_func(f"JSON 내보내기 완료: {path}")


def handle_json_import(prompts, output_func, root=None):
    try:
        imported_prompts = storage.import_json(root)
    except Exception as exc:
        output_func(f"JSON 가져오기 실패: {exc}")
        return
    prompts[:] = imported_prompts
    output_func(f"JSON 가져오기 완료: {len(prompts)}개")


def handle_markdown_export(prompts, output_func, root=None):
    try:
        paths = storage.export_markdown(prompts, root)
    except Exception as exc:
        output_func(f"Markdown 내보내기 실패: {exc}")
        return
    output_func(f"Markdown 내보내기 완료: {len(paths)}개")


def show_prompt_list_detail_flow(
    prompts,
    input_func,
    output_func,
    heading,
    include_category,
    include_usage=False,
    empty_message="저장된 프롬프트가 없습니다.",
):
    if not prompts:
        output_func(empty_message)
        return

    output_func(heading)
    print_prompt_rows(prompts, output_func, include_category, include_usage)
    selected = read_prompt_selection(prompts, input_func, output_func)
    if selected is not None:
        show_prompt_detail(selected, output_func)


MENU_ACTIONS = {
    "1": lambda prompts, input_func, output_func, _root: handle_add_prompt(
        prompts,
        input_func,
        output_func,
    ),
    "2": lambda prompts, input_func, output_func, _root: handle_list_prompts(
        prompts,
        input_func,
        output_func,
    ),
    "3": lambda prompts, input_func, output_func, _root: handle_category_view(
        prompts,
        input_func,
        output_func,
    ),
    "4": lambda prompts, input_func, output_func, _root: handle_search(
        prompts,
        input_func,
        output_func,
    ),
    "5": lambda prompts, input_func, output_func, _root: handle_detail_view(
        prompts,
        input_func,
        output_func,
    ),
    "6": lambda prompts, input_func, output_func, _root: handle_favorite_toggle(
        prompts,
        input_func,
        output_func,
    ),
    "7": lambda prompts, input_func, output_func, _root: handle_favorites(
        prompts,
        input_func,
        output_func,
    ),
    "8": lambda prompts, input_func, output_func, _root: handle_update(
        prompts,
        input_func,
        output_func,
    ),
    "9": lambda prompts, input_func, output_func, _root: handle_delete(
        prompts,
        input_func,
        output_func,
    ),
    "10": lambda prompts, input_func, output_func, _root: handle_usage_sorted(
        prompts,
        input_func,
        output_func,
    ),
    "11": lambda prompts, _input_func, output_func, root: handle_json_export(
        prompts,
        output_func,
        root,
    ),
    "12": lambda prompts, _input_func, output_func, root: handle_json_import(
        prompts,
        output_func,
        root,
    ),
    "13": lambda prompts, _input_func, output_func, root: handle_markdown_export(
        prompts,
        output_func,
        root,
    ),
}
