# main.py
# 命令行结构化日记系统主入口
# 负责主流程调度，调用 ConsoleUI 进行交互，调用 DiaryService 处理业务逻辑

import sys
from service.diary_service import DiaryService
from ui.console import ConsoleUI

def main():
    """
    程序主入口：
    1. 获取用户名，初始化服务
    2. 循环显示菜单，根据用户选择执行新建记录、查看历史或退出
    """
    ui = ConsoleUI()
    service = DiaryService()
    username = ui.get_username()
    if not username:
        ui.show_invalid_username()
        return
    service.set_user(username)
    while True:
        choice = ui.show_menu()
        if choice == '1':
            today = service.today()
            if service.has_today_record():
                ui.show_today_exists(today)
                continue
            record = ui.get_diary_input(today, service.get_questions())
            service.add_record(record)
            ui.show_save_success()
        elif choice == '2':
            records = service.get_all_records()
            ui.show_history(records)
        elif choice == '0':
            ui.exit()
            break
        else:
            ui.show_invalid_choice()

if __name__ == "__main__":
    main()
