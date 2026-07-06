from constants import EDITABLE_PROMPT_FIELDS, PROMPT_FIELDS
from utils import normalize_required_text

STANDARD_FIELDS = PROMPT_FIELDS
EDITABLE_FIELDS = EDITABLE_PROMPT_FIELDS


def create_starter_prompts():
    return [
        _create_prompt(
            "블로그 글 구조화",
            "주제를 바탕으로 독자가 이해하기 쉬운 블로그 글 개요를 작성해줘.",
            "text",
        ),
        _create_prompt(
            "이미지 생성 장면 묘사",
            "피사체, 배경, 조명, 스타일을 포함해 이미지 생성 프롬프트를 다듬어줘.",
            "image",
        ),
        _create_prompt(
            "업무 자동화 페르소나",
            "반복 업무를 자동화하는 신중한 운영 담당자 관점으로 절차를 정리해줘.",
            "automation",
        ),
    ]


def add_prompt(prompts, title, content, category):
    prompt = _create_prompt(title, content, category)
    prompts.append(prompt)
    return prompt


def list_categories(prompts):
    categories = []
    seen = set()
    for prompt in prompts:
        category = prompt["category"]
        if category not in seen:
            categories.append(category)
            seen.add(category)
    return categories


def filter_by_category(prompts, category):
    return [prompt for prompt in prompts if prompt["category"] == category]


def search_prompts(prompts, keyword):
    normalized_keyword = keyword.casefold()
    return [
        prompt
        for prompt in prompts
        if normalized_keyword in prompt["title"].casefold()
        or normalized_keyword in prompt["content"].casefold()
    ]


def record_detail_view(prompt):
    prompt["usage_count"] += 1
    return prompt


def toggle_favorite(prompt):
    prompt["favorite"] = not prompt["favorite"]
    return prompt["favorite"]


def favorite_prompts(prompts):
    return [prompt for prompt in prompts if prompt["favorite"]]


def update_prompt_field(prompt, field_name, value):
    if field_name not in EDITABLE_FIELDS:
        raise ValueError("수정할 수 없는 필드입니다.")
    prompt[field_name] = normalize_required_text(value)
    return prompt


def select_prompt_by_number(prompts, number):
    index = _prompt_index_from_number(prompts, number, allow_cancel=True)
    if index is None:
        return None
    return prompts[index]


def delete_prompt_by_number(prompts, number):
    return prompts.pop(_prompt_index_from_number(prompts, number))


def sort_by_usage_count(prompts):
    return [
        prompt
        for _, prompt in sorted(
            enumerate(prompts),
            key=lambda indexed_prompt: (
                -indexed_prompt[1]["usage_count"],
                indexed_prompt[0],
            ),
        )
    ]


def _create_prompt(title, content, category, favorite=False, usage_count=0):
    return {
        "title": normalize_required_text(title),
        "content": normalize_required_text(content),
        "category": normalize_required_text(category),
        "favorite": favorite,
        "usage_count": usage_count,
    }


def _prompt_index_from_number(prompts, number, allow_cancel=False):
    if number == 0 and allow_cancel:
        return None
    if number < 1 or number > len(prompts):
        raise IndexError("목록 번호가 범위를 벗어났습니다.")
    return number - 1
