import archive
from console_io import read_prompt_selection


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
