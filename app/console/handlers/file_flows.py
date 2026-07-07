import storage


def handle_json_export(prompts, output_func, root=None):
    try:
        path = storage.export_json(prompts, root)
    except Exception as exc:
        output_func(f"JSON 내보내기 실패: {exc}")
        return
    output_func(f"JSON 내보내기 완료: {path}")


def handle_json_import(prompts, output_func, root=None):
    try:
        imported_prompts = storage.import_json(root)
    except Exception as exc:
        output_func(f"JSON 가져오기 실패: {exc}")
        return
    prompts[:] = imported_prompts
    output_func(f"JSON 가져오기 완료: {len(prompts)}개")


def handle_markdown_export(prompts, output_func, root=None):
    try:
        paths = storage.export_markdown(prompts, root)
    except Exception as exc:
        output_func(f"Markdown 내보내기 실패: {exc}")
        return
    output_func(f"Markdown 내보내기 완료: {len(paths)}개")
