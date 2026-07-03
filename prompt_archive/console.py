from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from prompt_archive.markdown_export import MarkdownExportError, export_markdown
from prompt_archive.prompts import (
    Prompt,
    add_prompt,
    delete_prompt,
    edit_prompt_field,
    favorite_prompts,
    filter_by_category,
    get_categories,
    search_prompts,
    starter_prompts,
    toggle_favorite,
    usage_sorted_prompts,
    view_prompt,
)
from prompt_archive.storage import JSONImportError, export_json, replace_prompts_from_json


InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]

MENU_ITEMS = [
    "Add prompt",
    "List prompts",
    "Browse by category",
    "Search prompts",
    "View detail",
    "Manage favorites",
    "Favorite prompts",
    "Edit prompt",
    "Delete prompt",
    "Sort by usage count",
    "Export JSON",
    "Import JSON",
    "Export Markdown",
    "Exit",
]


def run_app(
    prompts: list[Prompt] | None = None,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
    data_dir: Path | str = Path("data"),
) -> list[Prompt]:
    active_prompts = starter_prompts() if prompts is None else prompts
    data_path = Path(data_dir)
    while True:
        _show_menu(output_func)
        choice = _read_number(input_func, "Select an option: ")
        if choice is None or choice < 1 or choice > len(MENU_ITEMS):
            output_func("Invalid choice. Please enter a listed number.")
            continue
        if choice == 1:
            _add_prompt_flow(active_prompts, input_func, output_func)
        elif choice == 2:
            _list_prompt_flow(active_prompts, input_func, output_func)
        elif choice == 3:
            _category_flow(active_prompts, input_func, output_func)
        elif choice == 4:
            _search_flow(active_prompts, input_func, output_func)
        elif choice == 5:
            _detail_flow(active_prompts, input_func, output_func)
        elif choice == 6:
            _favorite_toggle_flow(active_prompts, input_func, output_func)
        elif choice == 7:
            _favorite_list_flow(active_prompts, input_func, output_func)
        elif choice == 8:
            _edit_flow(active_prompts, input_func, output_func)
        elif choice == 9:
            _delete_flow(active_prompts, input_func, output_func)
        elif choice == 10:
            _usage_sorted_flow(active_prompts, input_func, output_func)
        elif choice == 11:
            _export_json_flow(active_prompts, data_path, output_func)
        elif choice == 12:
            _import_json_flow(active_prompts, data_path, output_func)
        elif choice == 13:
            _export_markdown_flow(active_prompts, data_path, output_func)
        else:
            output_func("Goodbye.")
            return active_prompts


def _show_menu(output_func: OutputFunc) -> None:
    output_func("")
    output_func("Simple Prompt Archive")
    for index, item in enumerate(MENU_ITEMS, start=1):
        output_func(f"{index}. {item}")


def _add_prompt_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    title = _read_required(input_func, output_func, "Title: ", "Title is required.")
    content = _read_required(input_func, output_func, "Content: ", "Content is required.")
    category = _read_required(input_func, output_func, "Category: ", "Category is required.")
    add_prompt(prompts, title, content, category)
    output_func("Prompt added.")


def _list_prompt_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    _select_and_view(prompts, prompts, input_func, output_func, include_category=True)


def _category_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    if not prompts:
        output_func("No prompts available.")
        return
    categories = get_categories(prompts)
    output_func("Categories")
    for index, category in enumerate(categories, start=1):
        output_func(f"{index}. {category}")
    output_func("0. Return to main menu")
    selected_index = _read_selection(input_func, output_func, len(categories), "Select a category number: ")
    if selected_index is None:
        return
    selected_category = categories[selected_index]
    category_prompts = filter_by_category(prompts, selected_category)
    if not category_prompts:
        output_func("No prompts found.")
        return
    _select_and_view(prompts, category_prompts, input_func, output_func, include_category=False)


def _search_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    keyword = input_func("Keyword: ")
    results = search_prompts(prompts, keyword)
    if not results:
        output_func("No prompts found.")
        return
    output_func("Search results")
    for index, prompt in enumerate(results, start=1):
        output_func(_format_prompt_row(index, prompt, include_category=True, include_usage=False))


def _detail_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    _select_and_view(prompts, prompts, input_func, output_func, include_category=True)


def _favorite_toggle_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    selected_index = _select_prompt_index(prompts, input_func, output_func, include_category=True)
    if selected_index is None:
        return
    is_favorite = toggle_favorite(prompts[selected_index])
    output_func(f"Favorite is now {'on' if is_favorite else 'off'}.")


def _favorite_list_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    favorites = favorite_prompts(prompts)
    if not favorites:
        output_func("No favorite prompts.")
        return
    _select_and_view(prompts, favorites, input_func, output_func, include_category=True)


def _edit_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    selected_index = _select_prompt_index(prompts, input_func, output_func, include_category=True)
    if selected_index is None:
        return
    prompt = prompts[selected_index]
    fields = ["title", "content", "category"]
    output_func("Editable fields")
    for index, field in enumerate(fields, start=1):
        output_func(f"{index}. {field}")
    output_func("0. Return to main menu")
    field_index = _read_selection(input_func, output_func, len(fields), "Select a field number: ")
    if field_index is None:
        return
    new_value = _read_required(input_func, output_func, "New value: ", "New value is required.")
    edit_prompt_field(prompt, fields[field_index], new_value)
    output_func("Prompt updated.")


def _delete_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    selected_index = _select_prompt_index(prompts, input_func, output_func, include_category=True)
    if selected_index is None:
        return
    delete_prompt(prompts, selected_index)
    output_func("Prompt deleted.")


def _usage_sorted_flow(prompts: list[Prompt], input_func: InputFunc, output_func: OutputFunc) -> None:
    sorted_prompts = usage_sorted_prompts(prompts)
    _select_and_view(prompts, sorted_prompts, input_func, output_func, include_category=True, include_usage=True)


def _export_json_flow(prompts: list[Prompt], data_dir: Path, output_func: OutputFunc) -> None:
    try:
        export_json(prompts, data_dir / "prompts.json")
    except OSError as error:
        output_func(f"JSON export failed: {error}")
        return
    output_func("JSON exported.")


def _import_json_flow(prompts: list[Prompt], data_dir: Path, output_func: OutputFunc) -> None:
    try:
        replace_prompts_from_json(prompts, data_dir / "prompts.json")
    except JSONImportError as error:
        output_func(f"JSON import failed: {error}")
        return
    output_func("JSON imported.")


def _export_markdown_flow(prompts: list[Prompt], data_dir: Path, output_func: OutputFunc) -> None:
    try:
        export_markdown(prompts, data_dir)
    except (MarkdownExportError, OSError) as error:
        output_func(f"Markdown export failed: {error}")
        return
    output_func("Markdown exported.")


def _select_and_view(
    all_prompts: list[Prompt],
    displayed_prompts: list[Prompt],
    input_func: InputFunc,
    output_func: OutputFunc,
    include_category: bool,
    include_usage: bool = False,
) -> None:
    selected_index = _select_prompt_index(
        displayed_prompts,
        input_func,
        output_func,
        include_category=include_category,
        include_usage=include_usage,
    )
    if selected_index is None:
        return
    prompt = displayed_prompts[selected_index]
    if prompt not in all_prompts:
        output_func("Selected prompt is no longer available.")
        return
    _show_detail(prompt, output_func)


def _select_prompt_index(
    prompts: list[Prompt],
    input_func: InputFunc,
    output_func: OutputFunc,
    include_category: bool,
    include_usage: bool = False,
) -> int | None:
    if not prompts:
        output_func("No prompts available.")
        return None
    output_func("Prompts")
    for index, prompt in enumerate(prompts, start=1):
        output_func(_format_prompt_row(index, prompt, include_category=include_category, include_usage=include_usage))
    output_func("0. Return to main menu")
    return _read_selection(input_func, output_func, len(prompts), "Select a prompt number: ")


def _show_detail(prompt: Prompt, output_func: OutputFunc) -> None:
    view_prompt(prompt)
    output_func(f"Title: {prompt['title']}")
    output_func(f"Category: {prompt['category']}")
    output_func(f"Favorite: {'yes' if prompt['favorite'] else 'no'}")
    output_func(f"Usage count: {prompt['usage_count']}")
    output_func("Content:")
    output_func(str(prompt["content"]))


def _format_prompt_row(index: int, prompt: Prompt, include_category: bool, include_usage: bool) -> str:
    favorite_marker = " *" if prompt["favorite"] else ""
    category_part = f"[{prompt['category']}] " if include_category else ""
    usage_part = f" (views: {prompt['usage_count']})" if include_usage else ""
    return f"{index}. {category_part}{prompt['title']}{favorite_marker}{usage_part}"


def _read_required(
    input_func: InputFunc,
    output_func: OutputFunc,
    prompt: str,
    error_message: str,
) -> str:
    while True:
        value = input_func(prompt)
        if value.strip():
            return value
        output_func(error_message)


def _read_selection(
    input_func: InputFunc,
    output_func: OutputFunc,
    max_value: int,
    prompt: str,
) -> int | None:
    value = _read_number(input_func, prompt)
    if value == 0:
        output_func("Returning to main menu.")
        return None
    if value is None or value < 1 or value > max_value:
        output_func("Invalid choice. Please enter a listed number.")
        return None
    return value - 1


def _read_number(input_func: InputFunc, prompt: str) -> int | None:
    value = input_func(prompt).strip()
    try:
        return int(value)
    except ValueError:
        return None
