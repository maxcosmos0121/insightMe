import os
from datetime import datetime, timedelta
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

        class UserProfile(BaseModel):
            name = CharField(null=True)
            gender = CharField(null=True)
            birthday = DateField(null=True)
            monthly_income = CharField(null=True)
            monthly_expense = CharField(null=True)
            hobby = TextField(null=True)
            job = CharField(null=True)
            company = CharField(null=True)
            skills = TextField(null=True)

        self.Diary = Diary
        self.UserProfile = UserProfile
        self.db.connect(reuse_if_open=True)
        self.db.create_tables([self.Diary, self.UserProfile])

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

    def get_streak(self) -> int:
        """计算连续签到天数"""
        if not self.has_today_record():
            return 0
        
        streak = 0
        current_date = datetime.now().date()
        
        while True:
            # 检查当前日期是否有记录
            if self.Diary.select().where(self.Diary.date == current_date).exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak

    def get_today_mood(self) -> str:
        """获取今日心情"""
        if self.has_today_record():
            record = self.Diary.select().where(self.Diary.date == self.today()).first()
            return record.mood if record else '未填写'
        return '未填写'

    def get_profile(self) -> dict:
        profile = self.UserProfile.select().first()
        if profile:
            return {
                'name': profile.name,
                'gender': profile.gender,
                'birthday': profile.birthday.strftime('%Y-%m-%d') if profile.birthday else '',
                'monthly_income': profile.monthly_income,
                'monthly_expense': profile.monthly_expense,
                'hobby': profile.hobby,
                'job': profile.job,
                'company': profile.company,
                'skills': profile.skills
            }
        else:
            return {
                'name': '', 'gender': '', 'birthday': '', 'monthly_income': '', 'monthly_expense': '',
                'hobby': '', 'job': '', 'company': '', 'skills': ''
            }

    def save_profile(self, data: dict):
        profile = self.UserProfile.select().first()
        if not profile:
            profile = self.UserProfile.create(**data)
        else:
            for k, v in data.items():
                setattr(profile, k, v)
            profile.save()
