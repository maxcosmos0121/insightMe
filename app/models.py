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

        class Todo(BaseModel):
            id = AutoField(primary_key=True)
            content = TextField()  # 任务内容
            quadrant = CharField()  # 任务象限分类：重要紧急、重要不紧急、不重要紧急、不重要不紧急
            planned_start = DateTimeField(null=True)  # 计划开始时间
            planned_end = DateTimeField(null=True)  # 计划结束时间
            actual_start = DateTimeField(null=True)  # 实际开始时间
            actual_end = DateTimeField(null=True)  # 实际结束时间
            status = CharField(default='未开始')  # 执行状态：未开始、进行中、已完成、取消
            completion_note = TextField(null=True)  # 完成情况说明
            cancel_reason = TextField(null=True)  # 取消原因
            created_at = DateTimeField(default=datetime.now)  # 创建时间
            updated_at = DateTimeField(default=datetime.now)  # 更新时间

        self.Diary = Diary
        self.UserProfile = UserProfile
        self.Todo = Todo
        self.db.connect(reuse_if_open=True)
        self.db.create_tables([self.Diary, self.UserProfile, self.Todo])

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

    # 待做清单相关方法
    def add_todo(self, data: dict):
        """添加待做任务"""
        return self.Todo.create(**data)

    def get_all_todos(self) -> List[Dict]:
        """获取所有待做任务"""
        query = self.Todo.select().order_by(self.Todo.created_at.desc())
        return [
            {
                'id': todo.id,
                'content': todo.content,
                'quadrant': todo.quadrant,
                'planned_start': todo.planned_start.strftime('%Y-%m-%d %H:%M') if todo.planned_start else '',
                'planned_end': todo.planned_end.strftime('%Y-%m-%d %H:%M') if todo.planned_end else '',
                'actual_start': todo.actual_start.strftime('%Y-%m-%d %H:%M') if todo.actual_start else '',
                'actual_end': todo.actual_end.strftime('%Y-%m-%d %H:%M') if todo.actual_end else '',
                'status': todo.status,
                'completion_note': todo.completion_note,
                'cancel_reason': todo.cancel_reason,
                'created_at': todo.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': todo.updated_at.strftime('%Y-%m-%d %H:%M')
            }
            for todo in query
        ]

    def get_todo_by_id(self, todo_id: int) -> Dict:
        """根据ID获取待做任务"""
        todo = self.Todo.get_or_none(self.Todo.id == todo_id)
        if todo:
            return {
                'id': todo.id,
                'content': todo.content,
                'quadrant': todo.quadrant,
                'planned_start': todo.planned_start.strftime('%Y-%m-%d %H:%M') if todo.planned_start else '',
                'planned_end': todo.planned_end.strftime('%Y-%m-%d %H:%M') if todo.planned_end else '',
                'actual_start': todo.actual_start.strftime('%Y-%m-%d %H:%M') if todo.actual_start else '',
                'actual_end': todo.actual_end.strftime('%Y-%m-%d %H:%M') if todo.actual_end else '',
                'status': todo.status,
                'completion_note': todo.completion_note,
                'cancel_reason': todo.cancel_reason,
                'created_at': todo.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': todo.updated_at.strftime('%Y-%m-%d %H:%M')
            }
        return None

    def update_todo(self, todo_id: int, data: dict):
        """更新待做任务"""
        data['updated_at'] = datetime.now()
        todo = self.Todo.get_or_none(self.Todo.id == todo_id)
        if todo:
            for k, v in data.items():
                setattr(todo, k, v)
            todo.save()
            return True
        return False

    def delete_todo(self, todo_id: int):
        """删除待做任务"""
        todo = self.Todo.get_or_none(self.Todo.id == todo_id)
        if todo:
            todo.delete_instance()
            return True
        return False

    def get_todo_stats(self) -> Dict:
        """获取待做任务统计"""
        total = self.Todo.select().count()
        not_started = self.Todo.select().where(self.Todo.status == '未开始').count()
        in_progress = self.Todo.select().where(self.Todo.status == '进行中').count()
        completed = self.Todo.select().where(self.Todo.status == '已完成').count()
        cancelled = self.Todo.select().where(self.Todo.status == '取消').count()
        
        return {
            'total': total,
            'not_started': not_started,
            'in_progress': in_progress,
            'completed': completed,
            'cancelled': cancelled
        }
