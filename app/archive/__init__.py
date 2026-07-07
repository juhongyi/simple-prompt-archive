from constants import EDITABLE_PROMPT_FIELDS, PROMPT_FIELDS

from .prompts import (
    add_prompt,
    create_prompt,
    create_starter_prompts,
    record_detail_view,
    toggle_favorite,
    update_prompt_field,
)
from .queries import (
    favorite_prompts,
    filter_by_category,
    list_categories,
    search_prompts,
    sort_by_usage_count,
)
from .selection import (
    delete_prompt_by_number,
    prompt_index_from_number,
    select_prompt_by_number,
)

STANDARD_FIELDS = PROMPT_FIELDS
EDITABLE_FIELDS = EDITABLE_PROMPT_FIELDS

__all__ = [
    "EDITABLE_FIELDS",
    "STANDARD_FIELDS",
    "add_prompt",
    "create_prompt",
    "create_starter_prompts",
    "delete_prompt_by_number",
    "favorite_prompts",
    "filter_by_category",
    "list_categories",
    "prompt_index_from_number",
    "record_detail_view",
    "search_prompts",
    "select_prompt_by_number",
    "sort_by_usage_count",
    "toggle_favorite",
    "update_prompt_field",
]
