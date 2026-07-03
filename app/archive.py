STANDARD_FIELDS = ("title", "content", "category", "favorite", "usage_count")
EDITABLE_FIELDS = ("title", "content", "category")


def create_starter_prompts():
    return [
        {
            "title": "블로그 글 구조화",
            "content": "주제를 바탕으로 독자가 이해하기 쉬운 블로그 글 개요를 작성해줘.",
            "category": "text",
            "favorite": False,
            "usage_count": 0,
        },
        {
            "title": "이미지 생성 장면 묘사",
            "content": "피사체, 배경, 조명, 스타일을 포함해 이미지 생성 프롬프트를 다듬어줘.",
            "category": "image",
            "favorite": False,
            "usage_count": 0,
        },
        {
            "title": "업무 자동화 페르소나",
            "content": "반복 업무를 자동화하는 신중한 운영 담당자 관점으로 절차를 정리해줘.",
            "category": "automation",
            "favorite": False,
            "usage_count": 0,
        },
    ]


def normalize_required_text(value):
    normalized = value.strip()
    if not normalized:
        raise ValueError("필수 입력 항목은 비워둘 수 없습니다.")
    return normalized


def add_prompt(prompts, title, content, category):
    prompt = {
        "title": normalize_required_text(title),
        "content": normalize_required_text(content),
        "category": normalize_required_text(category),
        "favorite": False,
        "usage_count": 0,
    }
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
    if number == 0:
        return None
    if number < 1 or number > len(prompts):
        raise IndexError("목록 번호가 범위를 벗어났습니다.")
    return prompts[number - 1]


def delete_prompt_by_number(prompts, number):
    if number < 1 or number > len(prompts):
        raise IndexError("목록 번호가 범위를 벗어났습니다.")
    return prompts.pop(number - 1)


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
