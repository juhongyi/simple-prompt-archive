import json


def format_markdown_prompt(prompt):
    return (
        "---\n"
        f"title: {quote_frontmatter(prompt['title'])}\n"
        f"category: {quote_frontmatter(prompt['category'])}\n"
        f"favorite: {str(prompt['favorite']).lower()}\n"
        f"usage_count: {prompt['usage_count']}\n"
        "---\n\n"
        f"{prompt['content']}"
    )


def quote_frontmatter(value):
    return json.dumps(str(value), ensure_ascii=False)
