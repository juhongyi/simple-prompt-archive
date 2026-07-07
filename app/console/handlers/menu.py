from .file_flows import (
    handle_json_export,
    handle_json_import,
    handle_markdown_export,
)
from .mutation_flows import (
    handle_delete,
    handle_favorite_toggle,
    handle_favorites,
    handle_update,
)
from .prompt_flows import (
    handle_add_prompt,
    handle_category_view,
    handle_detail_view,
    handle_list_prompts,
    handle_search,
    handle_usage_sorted,
)

MENU_ACTIONS = {
    "1": lambda prompts, input_func, output_func, _root: handle_add_prompt(
        prompts,
        input_func,
        output_func,
    ),
    "2": lambda prompts, input_func, output_func, _root: handle_list_prompts(
        prompts,
        input_func,
        output_func,
    ),
    "3": lambda prompts, input_func, output_func, _root: handle_category_view(
        prompts,
        input_func,
        output_func,
    ),
    "4": lambda prompts, input_func, output_func, _root: handle_search(
        prompts,
        input_func,
        output_func,
    ),
    "5": lambda prompts, input_func, output_func, _root: handle_detail_view(
        prompts,
        input_func,
        output_func,
    ),
    "6": lambda prompts, input_func, output_func, _root: handle_favorite_toggle(
        prompts,
        input_func,
        output_func,
    ),
    "7": lambda prompts, input_func, output_func, _root: handle_favorites(
        prompts,
        input_func,
        output_func,
    ),
    "8": lambda prompts, input_func, output_func, _root: handle_update(
        prompts,
        input_func,
        output_func,
    ),
    "9": lambda prompts, input_func, output_func, _root: handle_delete(
        prompts,
        input_func,
        output_func,
    ),
    "10": lambda prompts, input_func, output_func, _root: handle_usage_sorted(
        prompts,
        input_func,
        output_func,
    ),
    "11": lambda prompts, _input_func, output_func, root: handle_json_export(
        prompts,
        output_func,
        root,
    ),
    "12": lambda prompts, _input_func, output_func, root: handle_json_import(
        prompts,
        output_func,
        root,
    ),
    "13": lambda prompts, _input_func, output_func, root: handle_markdown_export(
        prompts,
        output_func,
        root,
    ),
}
