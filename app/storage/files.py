import json

from constants import PROMPT_FIELDS, STORAGE_VERSION

from .errors import StorageError
from .paths import json_file_path


def standard_prompt(prompt):
    return {field: prompt[field] for field in PROMPT_FIELDS}


def export_json(prompts, root=None):
    path = json_file_path(root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(json_payload(prompts), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise StorageError("JSON 파일을 쓸 수 없습니다.") from exc
    return path


def import_json(root=None):
    path = json_file_path(root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise StorageError("JSON 파일을 읽을 수 없습니다.") from exc
    except json.JSONDecodeError as exc:
        raise StorageError("JSON 형식이 올바르지 않습니다.") from exc

    if payload.get("version") != STORAGE_VERSION:
        raise StorageError("지원하지 않는 JSON 버전입니다.")
    prompts = payload.get("prompts")
    if not isinstance(prompts, list):
        raise StorageError("prompts 배열이 없습니다.")

    for prompt in prompts:
        if not isinstance(prompt, dict):
            raise StorageError("프롬프트 항목은 객체여야 합니다.")
        missing_fields = [field for field in PROMPT_FIELDS if field not in prompt]
        if missing_fields:
            raise StorageError("프롬프트 항목에 필수 필드가 없습니다.")

    return [dict(prompt) for prompt in prompts]


def json_payload(prompts):
    return {
        "version": STORAGE_VERSION,
        "prompts": [standard_prompt(prompt) for prompt in prompts],
    }
