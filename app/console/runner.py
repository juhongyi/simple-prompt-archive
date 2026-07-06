import archive

from .handlers import MENU_ACTIONS
from .io import read_line
from .views import print_menu


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
            action = MENU_ACTIONS.get(choice)
            if action is None:
                output_func("올바른 메뉴 번호를 입력해주세요.")
            else:
                action(active_prompts, input_func, output_func, root)
        except EOFError:
            output_func("입력이 종료되어 프로그램을 종료합니다.")
            break

    return active_prompts
