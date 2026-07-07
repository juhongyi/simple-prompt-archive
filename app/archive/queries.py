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


def favorite_prompts(prompts):
    return [prompt for prompt in prompts if prompt["favorite"]]


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
