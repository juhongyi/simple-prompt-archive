def normalize_required_text(value):
    normalized = value.strip()
    if not normalized:
        raise ValueError("필수 입력 항목은 비워둘 수 없습니다.")
    return normalized


def slugify(value):
    slug_parts = []
    in_separator = False

    for char in value.strip():
        if is_allowed_slug_char(char):
            slug_parts.append(char.lower())
            in_separator = False
        elif not in_separator:
            slug_parts.append("-")
            in_separator = True

    return "".join(slug_parts).strip("-")


def is_allowed_slug_char(char):
    return (
        "0" <= char <= "9"
        or "a" <= char <= "z"
        or "A" <= char <= "Z"
        or "\uac00" <= char <= "\ud7a3"
    )
