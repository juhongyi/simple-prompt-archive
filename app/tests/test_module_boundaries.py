import archive
import console
import constants
import storage


def test_archive_and_storage_share_prompt_constants() -> None:
    assert archive.STANDARD_FIELDS is constants.PROMPT_FIELDS
    assert archive.EDITABLE_FIELDS is constants.EDITABLE_PROMPT_FIELDS
    assert storage.STANDARD_FIELDS is constants.PROMPT_FIELDS
    assert storage.VERSION == constants.STORAGE_VERSION
    assert storage.MAX_ORDER == constants.MAX_ORDER


def test_console_package_exports_existing_public_api() -> None:
    public_names = [
        "MENU_ITEMS",
        "EDIT_FIELD_CHOICES",
        "MENU_ACTIONS",
        "favorite_marker",
        "handle_add_prompt",
        "handle_json_export",
        "print_menu",
        "read_multiline_content",
        "read_prompt_selection",
        "run_app",
        "show_prompt_detail",
        "show_prompt_list_detail_flow",
    ]

    for public_name in public_names:
        assert hasattr(console, public_name)


def test_storage_package_exports_existing_public_api() -> None:
    public_names = [
        "StorageError",
        "project_root",
        "data_directory",
        "json_file_path",
        "standard_prompt",
        "export_json",
        "import_json",
        "slugify",
        "export_markdown",
        "VERSION",
        "STANDARD_FIELDS",
        "MAX_ORDER",
    ]

    for public_name in public_names:
        assert hasattr(storage, public_name)
