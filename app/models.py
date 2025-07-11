import os
from datetime import datetime
from typing import List, Dict

from peewee import *


class DiaryDB:
    def __init__(self, username: str):
        os.makedirs('users', exist_ok=True)
        db_path = os.path.join('users', f'{username}.db')
        self.db = SqliteDatabase(db_path)

        class BaseModel(Model):
            class Meta:
                database = self.db

        class Diary(BaseModel):
            date = DateField(primary_key=True)
            activities = TextField()
            income = TextField()
            expense = TextField()
            mood = TextField()
            thoughts = TextField()
            plan = TextField()

        self.Diary = Diary
        self.db.connect(reuse_if_open=True)
        self.db.create_tables([self.Diary])

    def today(self):
        return datetime.now().strftime('%Y-%m-%d')

    def has_today_record(self):
        return self.Diary.select().where(self.Diary.date == self.today()).exists()

    def get_questions(self):
        return [
            ('activities', '💬 做了什么'),
            ('income', '💰 收入'),
            ('expense', '💸 支出'),
            ('mood', '🙂 情绪评分'),
            ('thoughts', '💭 想法'),
            ('plan', '📌 明日计划')
        ]

    def add_record(self, record: Dict[str, str]):
        self.Diary.create(
            date=self.today(),
            activities=record['activities'],
            income=record['income'],
            expense=record['expense'],
            mood=record['mood'],
            thoughts=record['thoughts'],
            plan=record['plan']
        )

    def get_all_records(self) -> List[Dict[str, str]]:
        query = self.Diary.select().order_by(self.Diary.date.desc())
        return [
            {
                'date': rec.date.strftime('%Y-%m-%d'),
                'activities': rec.activities,
                'income': rec.income,
                'expense': rec.expense,
                'mood': rec.mood,
                'thoughts': rec.thoughts,
                'plan': rec.plan,
            }
            for rec in query
        ]
