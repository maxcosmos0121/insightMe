# ui/console.py
# 负责所有命令行输入输出（UI 层）

class ConsoleUI:
    """
    ConsoleUI 负责所有命令行交互，包括用户名输入、菜单、日记内容输入、历史记录展示等。
    """

    def get_username(self):
        """
        获取用户名输入。
        :return: 用户名字符串
        """
        username = input("请输入你的用户名（例如：xiaoming）：\n> ").strip()
        return username

    def show_menu(self):
        """
        显示主菜单并获取用户选择。
        :return: 用户选择的菜单项
        """
        print("\n=== 菜单 ===")
        print("1. 新建每日记录")
        print("2. 查看历史记录")
        print("0. 退出程序")
        return input("\n请选择：\n> ").strip()

    def get_diary_input(self, today, questions):
        """
        结构化提问，获取用户的日记内容。
        :param today: 今日日期字符串
        :param questions: [(问题, 字段名)] 列表
        :return: 填写好的记录 dict
        """
        print(f"\n📅 自动填入今日日期：{today}")
        record = {"date": today}
        for q, key in questions:
            if key in ("activities", "thoughts", "plan"):
                print(q + "（多行输入，输入空行结束）")
                lines = []
                while True:
                    line = input()
                    if line == "":
                        break
                    lines.append(line)
                ans = "\n".join(lines)
            else:
                ans = input(f"{q}\n> ").strip()
            record[key] = ans
        return record

    def show_save_success(self):
        """
        显示保存成功提示。
        """
        print("\n✅ 已保存！你的记录已经写入数据库")

    def show_history(self, records):
        """
        展示历史记录。
        :param records: 记录列表
        """
        if not records:
            print("\n暂无历史记录。")
            return
        print("\n=== 历史记录 ===\n")

        def pretty_multiline(label, content):
            lines = content.split('\n')
            print(f"{label}：")
            for l in lines:
                print(f"    {l}")

        for rec in records:
            print(f"📅 {rec['date']}")
            pretty_multiline("💬 做了什么", rec['activities'])
            print(f"💰 收入：{rec['income']}")
            print(f"💸 支出：{rec['expense']}")
            print(f"🙂 情绪评分：{rec['mood']}")
            pretty_multiline("💭 想法", rec['thoughts'])
            pretty_multiline("📌 明日计划", rec['plan'])
            print("-" * 28)

    def show_today_exists(self, today):
        """
        提示今日已存在记录。
        :param today: 今日日期字符串
        """
        print(f"\n⚠️ 今天（{today}）的记录已存在，不能重复填写。")

    def show_invalid_username(self):
        """
        提示用户名不能为空。
        """
        print("用户名不能为空！")

    def show_invalid_choice(self):
        """
        提示无效菜单选择。
        """
        print("无效选择，请重新输入。")

    def exit(self):
        """
        退出提示。
        """
        print("\n再见！")
