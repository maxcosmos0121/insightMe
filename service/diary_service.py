# service/diary_service.py
# 负责业务逻辑处理（Service 层），如用户切换、数据存取、问题列表等

import os
from datetime import datetime

from utils.db_helper import DiaryDB


class DiaryService:
    """
    DiaryService 负责业务流程，包括设置用户、添加记录、获取历史记录、判断今日是否已记录等。
    """
    USERS_DIR = 'users'
    QUESTIONS = [
        ("今天做了什么？", "activities"),
        ("今天收入了多少钱？（可填0）", "income"),
        ("今天支出了多少钱？（可填0）", "expense"),
        ("你的情绪评分（0-10）？", "mood"),
        ("有什么想法或总结？", "thoughts"),
        ("明天打算做什么？", "plan"),
    ]
    def __init__(self):
        """
        初始化 DiaryService。
        """
        self.db = None
        self.username = None

    def set_user(self, username):
        """
        设置当前用户，初始化对应数据库。
        :param username: 用户名字符串
        """
        if not os.path.exists(self.USERS_DIR):
            os.makedirs(self.USERS_DIR)
        self.username = username
        db_path = os.path.join(self.USERS_DIR, f"{username}.db")
        self.db = DiaryDB(db_path)

    def today(self):
        """
        获取今日日期字符串。
        :return: 'YYYY-MM-DD' 格式日期
        """
        return datetime.now().strftime('%Y-%m-%d')

    def has_today_record(self):
        """
        判断今日是否已有记录。
        :return: bool
        """
        return self.db.has_record(self.today())

    def add_record(self, record):
        """
        添加一条日记记录。
        :param record: 记录 dict
        """
        self.db.add_record(record)

    def get_all_records(self):
        """
        获取所有历史记录。
        :return: 记录列表
        """
        return self.db.get_all_records()

    def get_questions(self):
        """
        获取结构化提问列表。
        :return: [(问题, 字段名)] 列表
        """
        return self.QUESTIONS
