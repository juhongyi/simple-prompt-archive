import archive


def read_line(input_func):
    return input_func()


def read_required_text(label, input_func, output_func):
    while True:
        output_func(f"{label}:")
        value = read_line(input_func).strip()
        if value:
            return value
        output_func("필수 입력 항목은 비워둘 수 없습니다.")


def read_multiline_content(input_func, output_func):
    while True:
        output_func("본문을 입력하세요. 단독 EOF 줄로 입력을 종료합니다:")
        lines = []
        while True:
            line = read_line(input_func)
            if line == "EOF":
                break
            lines.append(line)

        content = "\n".join(lines).strip()
        if content:
            return content
        output_func("필수 입력 항목은 비워둘 수 없습니다.")


def read_number(input_func):
    return int(read_line(input_func).strip())


def read_prompt_selection(prompts, input_func, output_func):
    output_func("프롬프트 번호를 입력하세요. 0은 메뉴로 돌아갑니다:")
    try:
        number = read_number(input_func)
        selected = archive.select_prompt_by_number(prompts, number)
    except ValueError:
        output_func("숫자를 입력해주세요.")
        return None
    except IndexError as exc:
        output_func(str(exc))
        return None

    if selected is None:
        output_func("메뉴로 돌아갑니다.")
    return selected
