from constants import EDITABLE_PROMPT_FIELDS
from utils import normalize_required_text


def create_prompt(title, content, category, favorite=False, usage_count=0):
    return {
        "title": normalize_required_text(title),
        "content": normalize_required_text(content),
        "category": normalize_required_text(category),
        "favorite": favorite,
        "usage_count": usage_count,
    }


def create_starter_prompts():
    return [
        create_prompt(
            "블로그 글 구조화",
            "주제를 바탕으로 독자가 이해하기 쉬운 블로그 글 개요를 작성해줘.",
            "text",
        ),
        create_prompt(
            "이미지 생성 장면 묘사",
            "피사체, 배경, 조명, 스타일을 포함해 이미지 생성 프롬프트를 다듬어줘.",
            "image",
        ),
        create_prompt(
            "업무 자동화 페르소나",
            "반복 업무를 자동화하는 신중한 운영 담당자 관점으로 절차를 정리해줘.",
            "automation",
        ),
    ]


def add_prompt(prompts, title, content, category):
    prompt = create_prompt(title, content, category)
    prompts.append(prompt)
    return prompt


def record_detail_view(prompt):
    prompt["usage_count"] += 1
    return prompt


def toggle_favorite(prompt):
    prompt["favorite"] = not prompt["favorite"]
    return prompt["favorite"]


def update_prompt_field(prompt, field_name, value):
    if field_name not in EDITABLE_PROMPT_FIELDS:
        raise ValueError("수정할 수 없는 필드입니다.")
    prompt[field_name] = normalize_required_text(value)
    return prompt
