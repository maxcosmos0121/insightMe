from typing import List, Dict

from peewee import *


class DiaryDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
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

    def add_record(self, record: Dict[str, str]):
        self.Diary.create(
            date=record['date'],
            activities=record['activities'],
            income=record['income'],
            expense=record['expense'],
            mood=record['mood'],
            thoughts=record['thoughts'],
            plan=record['plan']
        )

    def has_record(self, date: str) -> bool:
        return self.Diary.select().where(self.Diary.date == date).exists()

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
