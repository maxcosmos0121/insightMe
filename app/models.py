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
            content = TextField()  # 计划内容
            quadrant = CharField()  # 象限分类：重要紧急、重要不紧急、不重要紧急、不重要不紧急
            planned_start = DateTimeField(null=True)  # 计划开始时间
            planned_end = DateTimeField(null=True)  # 计划结束时间
            actual_start = DateTimeField(null=True)  # 实际开始时间
            actual_end = DateTimeField(null=True)  # 实际结束时间
            status = CharField(default='未开始')  # 执行状态：未开始、进行中、已完成、取消
            completion_note = TextField(null=True)  # 完成情况说明
            cancel_reason = TextField(null=True)  # 取消原因
            created_at = DateTimeField(default=datetime.now)  # 创建时间
            updated_at = DateTimeField(default=datetime.now)  # 更新时间

        class CheckinItem(BaseModel):
            id = AutoField(primary_key=True)
            title = CharField()  # 打卡项目标题
            description = TextField(null=True)  # 打卡项目描述
            frequency = CharField(default='daily')  # 打卡频率：daily(每日)、weekly(每周)、monthly(每月)
            target_days = IntegerField(default=0)  # 目标天数，0表示无限制
            icon = CharField(default='✅')  # 图标
            color = CharField(default='#3b82f6')  # 颜色主题
            is_active = BooleanField(default=True)  # 是否激活
            created_at = DateTimeField(default=datetime.now)  # 创建时间

        class CheckinRecord(BaseModel):
            id = AutoField(primary_key=True)
            item_id = ForeignKeyField(CheckinItem, backref='records')  # 关联的打卡项目
            checkin_date = DateField()  # 打卡日期
            note = TextField(null=True)  # 打卡备注
            mood = CharField(null=True)  # 打卡时的心情
            created_at = DateTimeField(default=datetime.now)  # 创建时间

        self.Diary = Diary
        self.UserProfile = UserProfile
        self.Todo = Todo
        self.CheckinItem = CheckinItem
        self.CheckinRecord = CheckinRecord
        self.db.connect(reuse_if_open=True)
        self.db.create_tables([self.Diary, self.UserProfile, self.Todo, self.CheckinItem, self.CheckinRecord])

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

    # 计划清单相关方法
    def add_todo(self, data: dict):
        """添加待做计划"""
        return self.Todo.create(**data)

    def get_all_todos(self) -> List[Dict]:
        """获取所有待做计划"""
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
        """根据ID获取待做计划"""
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
        """更新待做计划"""
        data['updated_at'] = datetime.now()
        todo = self.Todo.get_or_none(self.Todo.id == todo_id)
        if todo:
            for k, v in data.items():
                setattr(todo, k, v)
            todo.save()
            return True
        return False

    def delete_todo(self, todo_id: int):
        """删除待做计划"""
        todo = self.Todo.get_or_none(self.Todo.id == todo_id)
        if todo:
            todo.delete_instance()
            return True
        return False

    def get_todo_stats(self) -> Dict:
        """获取待做计划统计"""
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

    # 打卡相关方法
    def add_checkin_item(self, data: dict):
        """添加打卡项目"""
        return self.CheckinItem.create(**data)

    def get_all_checkin_items(self) -> List[Dict]:
        """获取所有打卡项目"""
        query = self.CheckinItem.select().order_by(self.CheckinItem.created_at.desc())
        items = []
        for item in query:
            # 计算每个项目的打卡统计
            total_records = self.CheckinRecord.select().where(self.CheckinRecord.item_id == item.id).count()
            today_checked = self.CheckinRecord.select().where(
                (self.CheckinRecord.item_id == item.id) & 
                (self.CheckinRecord.checkin_date == self.today())
            ).exists()
            
            items.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'frequency': item.frequency,
                'target_days': item.target_days,
                'icon': item.icon,
                'color': item.color,
                'is_active': item.is_active,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
                'total_records': total_records,
                'today_checked': today_checked
            })
        return items

    def get_checkin_item_by_id(self, item_id: int) -> Dict:
        """根据ID获取打卡项目"""
        item = self.CheckinItem.get_or_none(self.CheckinItem.id == item_id)
        if item:
            total_records = self.CheckinRecord.select().where(self.CheckinRecord.item_id == item.id).count()
            today_checked = self.CheckinRecord.select().where(
                (self.CheckinRecord.item_id == item.id) & 
                (self.CheckinRecord.checkin_date == self.today())
            ).exists()
            
            return {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'frequency': item.frequency,
                'target_days': item.target_days,
                'icon': item.icon,
                'color': item.color,
                'is_active': item.is_active,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
                'total_records': total_records,
                'today_checked': today_checked
            }
        return {}

    def update_checkin_item(self, item_id: int, data: dict):
        """更新打卡项目"""
        item = self.CheckinItem.get_or_none(self.CheckinItem.id == item_id)
        if item:
            for k, v in data.items():
                setattr(item, k, v)
            item.save()
            return True
        return False

    def delete_checkin_item(self, item_id: int):
        """删除打卡项目"""
        item = self.CheckinItem.get_or_none(self.CheckinItem.id == item_id)
        if item:
            # 先删除相关的打卡记录
            self.CheckinRecord.delete().where(self.CheckinRecord.item_id == item_id).execute()
            # 再删除打卡项目
            item.delete_instance()
            return True
        return False

    def add_checkin_record(self, item_id: int, note: str = None, mood: str = None):
        """添加打卡记录"""
        # 检查今天是否已经打卡
        if self.CheckinRecord.select().where(
            (self.CheckinRecord.item_id == item_id) & 
            (self.CheckinRecord.checkin_date == self.today())
        ).exists():
            return False, "今天已经打卡了"
        
        self.CheckinRecord.create(
            item_id=item_id,
            checkin_date=self.today(),
            note=note,
            mood=mood
        )
        return True, "打卡成功"

    def get_checkin_records(self, item_id: int = None, days: int = 30) -> List[Dict]:
        """获取打卡记录"""
        query = self.CheckinRecord.select()
        if item_id:
            query = query.where(self.CheckinRecord.item_id == item_id)
        
        # 限制查询天数
        start_date = datetime.now().date() - timedelta(days=days)
        query = query.where(self.CheckinRecord.checkin_date >= start_date)
        query = query.order_by(self.CheckinRecord.checkin_date.desc())
        
        records = []
        for record in query:
            item = self.CheckinItem.get_or_none(self.CheckinItem.id == record.item_id)
            records.append({
                'id': record.id,
                'item_id': record.item_id,
                'item_title': item.title if item else '未知项目',
                'item_icon': item.icon if item else '✅',
                'checkin_date': record.checkin_date.strftime('%Y-%m-%d'),
                'note': record.note,
                'mood': record.mood,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M')
            })
        return records

    def get_checkin_streak(self) -> int:
        """计算打卡连续天数"""
        # 获取所有打卡记录，按日期分组
        records = self.CheckinRecord.select(self.CheckinRecord.checkin_date).distinct()
        dates = [record.checkin_date for record in records]
        
        if not dates:
            return 0
        
        # 按日期排序
        dates.sort(reverse=True)
        
        # 计算连续天数
        streak = 0
        current_date = datetime.now().date()
        
        while current_date in dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak

    def get_checkin_stats(self) -> Dict:
        """获取打卡统计"""
        total_items = self.CheckinItem.select().where(self.CheckinItem.is_active == True).count()
        today_checked = 0
        total_records_today = 0
        
        if total_items > 0:
            # 计算今日已打卡项目数
            today_checked = self.CheckinRecord.select().where(
                self.CheckinRecord.checkin_date == self.today()
            ).count()
            total_records_today = total_items
        
        # 计算连续打卡天数（基于打卡记录）
        streak = self.get_checkin_streak()
        
        return {
            'total_items': total_items,
            'today_checked': today_checked,
            'total_records_today': total_records_today,
            'streak': streak
        }
