import archive

from ..io import (
    read_multiline_content,
    read_number,
    read_prompt_selection,
    read_required_text,
)
from ..views import print_prompt_rows, print_search_rows, show_prompt_detail


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
