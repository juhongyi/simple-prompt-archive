import archive

from .constants import MENU_ITEMS


def print_menu(output_func):
    output_func("")
    output_func("Simple Prompt Archive")
    for number, label in MENU_ITEMS:
        output_func(f"{number}. {label}")
    output_func("메뉴 번호를 입력하세요:")


def print_prompt_rows(prompts, output_func, include_category, include_usage=False):
    for index, prompt in enumerate(prompts, start=1):
        parts = [f"{index}."]
        if include_category:
            parts.append(f"[{prompt['category']}]")
        parts.append(prompt["title"])
        parts.append(favorite_marker(prompt))
        if include_usage:
            parts.append(f"(조회수: {prompt['usage_count']})")
        output_func(" ".join(parts))


def print_search_rows(prompts, output_func):
    for prompt in prompts:
        output_func(
            " ".join(
                [
                    "-",
                    f"[{prompt['category']}]",
                    prompt["title"],
                    favorite_marker(prompt),
                ]
            )
        )


def favorite_marker(prompt):
    return "★" if prompt["favorite"] else "☆"


def show_prompt_detail(prompt, output_func):
    archive.record_detail_view(prompt)
    output_func("프롬프트 상세")
    output_func(f"제목: {prompt['title']}")
    output_func(f"카테고리: {prompt['category']}")
    output_func(f"즐겨찾기: {'예' if prompt['favorite'] else '아니오'}")
    output_func(f"조회수: {prompt['usage_count']}")
    output_func("본문:")
    output_func(prompt["content"])
