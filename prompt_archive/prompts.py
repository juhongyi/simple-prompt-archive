from __future__ import annotations

from typing import Any


Prompt = dict[str, Any]

REQUIRED_FIELDS = ("title", "content", "category")
EDITABLE_FIELDS = set(REQUIRED_FIELDS)


def starter_prompts() -> list[Prompt]:
    return [
        {
            "title": "Sharper writing assistant",
            "content": "Rewrite the following text to be clear, concise, and useful while preserving the original meaning.",
            "category": "Writing",
            "favorite": False,
            "usage_count": 0,
        },
        {
            "title": "Image concept generator",
            "content": "Create a detailed image prompt with subject, setting, lighting, composition, and style notes.",
            "category": "Image",
            "favorite": False,
            "usage_count": 0,
        },
        {
            "title": "Automation planner",
            "content": "Act as an automation strategist and turn this repeated task into clear triggers, steps, and checks.",
            "category": "Automation",
            "favorite": False,
            "usage_count": 0,
        },
    ]


def add_prompt(prompts: list[Prompt], title: str, content: str, category: str) -> Prompt:
    _require_non_blank("title", title)
    _require_non_blank("content", content)
    _require_non_blank("category", category)
    prompt = {
        "title": title,
        "content": content,
        "category": category,
        "favorite": False,
        "usage_count": 0,
    }
    prompts.append(prompt)
    return prompt


def get_categories(prompts: list[Prompt]) -> list[str]:
    categories = []
    seen = set()
    for prompt in prompts:
        category = prompt["category"]
        if category not in seen:
            categories.append(category)
            seen.add(category)
    return categories


def filter_by_category(prompts: list[Prompt], category: str) -> list[Prompt]:
    return [prompt for prompt in prompts if prompt["category"] == category]


def search_prompts(prompts: list[Prompt], keyword: str) -> list[Prompt]:
    normalized_keyword = keyword.casefold()
    return [
        prompt
        for prompt in prompts
        if normalized_keyword in str(prompt["title"]).casefold()
        or normalized_keyword in str(prompt["content"]).casefold()
    ]


def view_prompt(prompt: Prompt) -> Prompt:
    prompt["usage_count"] += 1
    return prompt


def toggle_favorite(prompt: Prompt) -> bool:
    prompt["favorite"] = not prompt["favorite"]
    return prompt["favorite"]


def favorite_prompts(prompts: list[Prompt]) -> list[Prompt]:
    return [prompt for prompt in prompts if prompt["favorite"] is True]


def edit_prompt_field(prompt: Prompt, field: str, value: str) -> None:
    if field not in EDITABLE_FIELDS:
        raise ValueError(f"{field} cannot be edited")
    _require_non_blank(field, value)
    prompt[field] = value


def delete_prompt(prompts: list[Prompt], index: int) -> Prompt:
    return prompts.pop(index)


def usage_sorted_prompts(prompts: list[Prompt]) -> list[Prompt]:
    return sorted(prompts, key=lambda prompt: prompt["usage_count"], reverse=True)


def _require_non_blank(field: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} is required")
