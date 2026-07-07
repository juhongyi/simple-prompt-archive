def prompt_index_from_number(prompts, number, allow_cancel=False):
    if number == 0 and allow_cancel:
        return None
    if number < 1 or number > len(prompts):
        raise IndexError("목록 번호가 범위를 벗어났습니다.")
    return number - 1


def select_prompt_by_number(prompts, number):
    index = prompt_index_from_number(prompts, number, allow_cancel=True)
    if index is None:
        return None
    return prompts[index]


def delete_prompt_by_number(prompts, number):
    return prompts.pop(prompt_index_from_number(prompts, number))
