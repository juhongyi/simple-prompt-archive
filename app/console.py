import archive
import storage


MENU_ITEMS = (
    ("1", "프롬프트 추가"),
    ("2", "목록 보기"),
    ("3", "카테고리별 조회"),
    ("4", "검색"),
    ("5", "상세 보기"),
    ("6", "즐겨찾기 관리"),
    ("7", "즐겨찾기 목록"),
    ("8", "수정"),
    ("9", "삭제"),
    ("10", "조회수 정렬 목록"),
    ("11", "JSON 내보내기"),
    ("12", "JSON 가져오기"),
    ("13", "Markdown 내보내기"),
    ("0", "종료"),
)

EDIT_FIELD_CHOICES = {
    1: ("title", "제목"),
    2: ("content", "본문"),
    3: ("category", "카테고리"),
}


def run_app(input_func=input, output_func=print, root=None, prompts=None):
    active_prompts = prompts if prompts is not None else archive.create_starter_prompts()

    while True:
        print_menu(output_func)
        try:
            choice = read_line(input_func).strip()
        except EOFError:
            output_func("입력이 종료되어 프로그램을 종료합니다.")
            break

        if choice == "0":
            output_func("프로그램을 종료합니다.")
            break
        try:
            if choice == "1":
                handle_add_prompt(active_prompts, input_func, output_func)
            elif choice == "2":
                handle_list_prompts(active_prompts, input_func, output_func)
            elif choice == "3":
                handle_category_view(active_prompts, input_func, output_func)
            elif choice == "4":
                handle_search(active_prompts, input_func, output_func)
            elif choice == "5":
                handle_detail_view(active_prompts, input_func, output_func)
            elif choice == "6":
                handle_favorite_toggle(active_prompts, input_func, output_func)
            elif choice == "7":
                handle_favorites(active_prompts, input_func, output_func)
            elif choice == "8":
                handle_update(active_prompts, input_func, output_func)
            elif choice == "9":
                handle_delete(active_prompts, input_func, output_func)
            elif choice == "10":
                handle_usage_sorted(active_prompts, input_func, output_func)
            elif choice == "11":
                handle_json_export(active_prompts, output_func, root)
            elif choice == "12":
                handle_json_import(active_prompts, output_func, root)
            elif choice == "13":
                handle_markdown_export(active_prompts, output_func, root)
            else:
                output_func("올바른 메뉴 번호를 입력해주세요.")
        except EOFError:
            output_func("입력이 종료되어 프로그램을 종료합니다.")
            break

    return active_prompts


def print_menu(output_func):
    output_func("")
    output_func("Simple Prompt Archive")
    for number, label in MENU_ITEMS:
        output_func(f"{number}. {label}")
    output_func("메뉴 번호를 입력하세요:")


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


def handle_add_prompt(prompts, input_func, output_func):
    title = read_required_text("제목", input_func, output_func)
    content = read_multiline_content(input_func, output_func)
    category = read_required_text("카테고리", input_func, output_func)
    archive.add_prompt(prompts, title, content, category)
    output_func("프롬프트를 추가했습니다.")


def handle_list_prompts(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    output_func("전체 프롬프트 목록")
    print_prompt_rows(prompts, output_func, include_category=True)
    selected = read_prompt_selection(prompts, input_func, output_func)
    if selected is not None:
        show_prompt_detail(selected, output_func)


def handle_category_view(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    categories = archive.list_categories(prompts)
    output_func("카테고리 목록")
    for index, category in enumerate(categories, start=1):
        output_func(f"{index}. {category}")
    output_func("카테고리 번호를 입력하세요. 0은 메뉴로 돌아갑니다:")

    try:
        number = read_number(input_func)
        if number == 0:
            output_func("메뉴로 돌아갑니다.")
            return
        if number < 1 or number > len(categories):
            raise IndexError("목록 번호가 범위를 벗어났습니다.")
    except ValueError:
        output_func("숫자를 입력해주세요.")
        return
    except IndexError as exc:
        output_func(str(exc))
        return

    category_prompts = archive.filter_by_category(prompts, categories[number - 1])
    if not category_prompts:
        output_func("결과가 없습니다.")
        return

    output_func(f"{categories[number - 1]} 프롬프트 목록")
    print_prompt_rows(category_prompts, output_func, include_category=False)
    selected = read_prompt_selection(category_prompts, input_func, output_func)
    if selected is not None:
        show_prompt_detail(selected, output_func)


def handle_search(prompts, input_func, output_func):
    keyword = read_required_text("검색어", input_func, output_func)
    results = archive.search_prompts(prompts, keyword)
    if not results:
        output_func("검색 결과가 없습니다.")
        return

    output_func("검색 결과")
    print_search_rows(results, output_func)


def handle_detail_view(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    output_func("상세 보기 프롬프트 목록")
    print_prompt_rows(prompts, output_func, include_category=True)
    selected = read_prompt_selection(prompts, input_func, output_func)
    if selected is not None:
        show_prompt_detail(selected, output_func)


def handle_favorite_toggle(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    output_func("즐겨찾기 관리")
    print_prompt_rows(prompts, output_func, include_category=True)
    selected = read_prompt_selection(prompts, input_func, output_func)
    if selected is None:
        return

    enabled = archive.toggle_favorite(selected)
    state = "설정" if enabled else "해제"
    output_func(f"즐겨찾기 {state}: {selected['title']}")


def handle_favorites(prompts, input_func, output_func):
    favorites = archive.favorite_prompts(prompts)
    if not favorites:
        output_func("즐겨찾기된 프롬프트가 없습니다.")
        return

    output_func("즐겨찾기 목록")
    print_prompt_rows(favorites, output_func, include_category=True)
    selected = read_prompt_selection(favorites, input_func, output_func)
    if selected is not None:
        show_prompt_detail(selected, output_func)


def handle_update(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    output_func("수정할 프롬프트 목록")
    print_prompt_rows(prompts, output_func, include_category=True)
    selected = read_prompt_selection(prompts, input_func, output_func)
    if selected is None:
        return

    output_func("수정할 필드를 선택하세요.")
    for number, (_, label) in EDIT_FIELD_CHOICES.items():
        output_func(f"{number}. {label}")
    output_func("0. 메뉴로 돌아가기")

    try:
        field_number = read_number(input_func)
    except ValueError:
        output_func("숫자를 입력해주세요.")
        return

    if field_number == 0:
        output_func("메뉴로 돌아갑니다.")
        return
    if field_number not in EDIT_FIELD_CHOICES:
        output_func("올바른 수정 필드 번호를 입력해주세요.")
        return

    field_name, label = EDIT_FIELD_CHOICES[field_number]
    if field_name == "content":
        value = read_multiline_content(input_func, output_func)
    else:
        value = read_required_text(label, input_func, output_func)
    archive.update_prompt_field(selected, field_name, value)
    output_func("프롬프트를 수정했습니다.")


def handle_delete(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    output_func("삭제할 프롬프트 목록")
    print_prompt_rows(prompts, output_func, include_category=True)
    output_func("프롬프트 번호를 입력하세요. 0은 메뉴로 돌아갑니다:")

    try:
        number = read_number(input_func)
        if number == 0:
            output_func("메뉴로 돌아갑니다.")
            return
        deleted = archive.delete_prompt_by_number(prompts, number)
    except ValueError:
        output_func("숫자를 입력해주세요.")
        return
    except IndexError as exc:
        output_func(str(exc))
        return

    output_func(f"프롬프트를 삭제했습니다: {deleted['title']}")


def handle_usage_sorted(prompts, input_func, output_func):
    if not prompts:
        output_func("저장된 프롬프트가 없습니다.")
        return

    sorted_prompts = archive.sort_by_usage_count(prompts)
    output_func("조회수 정렬 목록")
    print_prompt_rows(
        sorted_prompts,
        output_func,
        include_category=True,
        include_usage=True,
    )
    selected = read_prompt_selection(sorted_prompts, input_func, output_func)
    if selected is not None:
        show_prompt_detail(selected, output_func)


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


def read_number(input_func):
    return int(read_line(input_func).strip())


def print_prompt_rows(prompts, output_func, include_category, include_usage=False):
    for index, prompt in enumerate(prompts, start=1):
        parts = [f"{index}."]
        if include_category:
            parts.append(f"[{prompt['category']}]")
        parts.append(prompt["title"])
        parts.append(favorite_marker(prompt))
        if include_usage:
            parts.append(f"(조회수: {prompt['usage_count']})")
        output_func(" ".join(parts))


def print_search_rows(prompts, output_func):
    for prompt in prompts:
        output_func(
            " ".join(
                [
                    "-",
                    f"[{prompt['category']}]",
                    prompt["title"],
                    favorite_marker(prompt),
                ]
            )
        )


def favorite_marker(prompt):
    return "★" if prompt["favorite"] else "☆"


def show_prompt_detail(prompt, output_func):
    archive.record_detail_view(prompt)
    output_func("프롬프트 상세")
    output_func(f"제목: {prompt['title']}")
    output_func(f"카테고리: {prompt['category']}")
    output_func(f"즐겨찾기: {'예' if prompt['favorite'] else '아니오'}")
    output_func(f"조회수: {prompt['usage_count']}")
    output_func("본문:")
    output_func(prompt["content"])
