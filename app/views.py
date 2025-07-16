from flask import Blueprint, render_template, request, redirect, url_for, session

from app.auth import UserAuth
from app.models import DiaryDB

diary_db = None
user_auth = UserAuth()
main_bp = Blueprint('main', __name__)


@main_bp.before_request
def before_request():
    global diary_db
    username = session.get('username')
    if username:
        diary_db = DiaryDB(username)
    else:
        diary_db = None


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not username or not password or not confirm_password:
            return render_template('auth/register.html', error='所有字段都必须填写')

        if password != confirm_password:
            return render_template('auth/register.html', error='两次输入的密码不一致')

        success, message = user_auth.register_user(username, password)
        if success:
            return redirect(url_for('main.login', registered='true'))
        else:
            return render_template('auth/register.html', error=message)

    return render_template('auth/register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('auth/login.html', error='用户名和密码不能为空')

        success, message = user_auth.verify_user(username, password)
        if success:
            session['username'] = username
            return redirect(url_for('main.home'))
        else:
            return render_template('auth/login.html', error=message)

    # 检查是否是从注册页面跳转过来的
    registered = request.args.get('registered')
    success_message = None
    if registered == 'true':
        success_message = '注册成功！请使用您的用户名和密码登录。'

    return render_template('auth/login.html', success=success_message)


@main_bp.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    # 获取用户信息
    user = {
        'username': session['username'],
        'nickname': diary_db.get_profile().get('name', '') if diary_db else '',
        'diary_count': len(diary_db.get_all_records()) if diary_db else 0,
        'streak': diary_db.get_streak() if diary_db else 0,
        'today_mood': diary_db.get_today_mood() if diary_db else '未填写',
        'todo_stats': diary_db.get_todo_stats() if diary_db else {'total': 0, 'not_started': 0, 'in_progress': 0, 'completed': 0, 'cancelled': 0},
        'checkin_stats': diary_db.get_checkin_stats() if diary_db else {'total_items': 0, 'today_checked': 0, 'total_records_today': 0, 'streak': 0}
    }
    return render_template('common/home.html', user=user)


@main_bp.route('/diary', methods=['GET', 'POST'])
def diary():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    today = diary_db.today()
    questions = diary_db.get_questions()
    if request.method == 'POST':
        if diary_db.has_today_record():
            return render_template('diary/diary.html', today=today, questions=questions, error='今天已经写过日记了')
        record = {key: request.form.get(key, '') for key, _ in questions}
        diary_db.add_record(record)
        return redirect(url_for('main.history'))
    return render_template('diary/diary.html', today=today, questions=questions)


@main_bp.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    records = diary_db.get_all_records()
    return render_template('diary/history.html', records=records)


@main_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        data = {
            'name': request.form.get('name', ''),
            'gender': request.form.get('gender', ''),
            'birthday': request.form.get('birthday', '') or None,
            'monthly_income': request.form.get('monthly_income', ''),
            'monthly_expense': request.form.get('monthly_expense', ''),
            'hobby': request.form.get('hobby', ''),
            'job': request.form.get('job', ''),
            'company': request.form.get('company', ''),
            'skills': request.form.get('skills', ''),
        }
        diary_db.save_profile(data)
        message = '保存成功！'
        profile = diary_db.get_profile()
        return render_template('auth/profile.html', profile=profile, message=message)
    else:
        profile = diary_db.get_profile()
        return render_template('auth/profile.html', profile=profile)


@main_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.login'))

# 计划清单相关路由
@main_bp.route('/todos')
def todos():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    # 获取筛选参数
    status_filter = request.args.get('status', '')

    # 获取所有计划并根据状态筛选
    all_todos = diary_db.get_all_todos()
    if status_filter:
        todos = [todo for todo in all_todos if todo['status'] == status_filter]
    else:
        todos = all_todos

    stats = diary_db.get_todo_stats()
    return render_template('todo/todos.html', todos=todos, stats=stats, current_filter=status_filter)


@main_bp.route('/todos/add', methods=['GET', 'POST'])
def add_todo():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        from datetime import datetime

        # 处理时间字段
        planned_start = request.form.get('planned_start')
        planned_end = request.form.get('planned_end')

        data = {
            'content': request.form.get('content', ''),
            'quadrant': request.form.get('quadrant', ''),
            'planned_start': datetime.strptime(planned_start, '%Y-%m-%dT%H:%M') if planned_start else None,
            'planned_end': datetime.strptime(planned_end, '%Y-%m-%dT%H:%M') if planned_end else None,
            'status': '未开始'
        }

        diary_db.add_todo(data)
        return redirect(url_for('main.todos'))

    return render_template('todo/add_todo.html')


@main_bp.route('/todos/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        from datetime import datetime

        # 处理时间字段
        planned_start = request.form.get('planned_start')
        planned_end = request.form.get('planned_end')

        data = {
            'content': request.form.get('content', ''),
            'quadrant': request.form.get('quadrant', ''),
            'planned_start': datetime.strptime(planned_start, '%Y-%m-%dT%H:%M') if planned_start else None,
            'planned_end': datetime.strptime(planned_end, '%Y-%m-%dT%H:%M') if planned_end else None,
            'status': request.form.get('status', '')
        }

        diary_db.update_todo(todo_id, data)
        return redirect(url_for('main.todos'))

    todo = diary_db.get_todo_by_id(todo_id)
    if not todo:
        return redirect(url_for('main.todos'))

    return render_template('todo/edit_todo.html', todo=todo)


@main_bp.route('/todos/delete/<int:todo_id>')
def delete_todo(todo_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    diary_db.delete_todo(todo_id)
    return redirect(url_for('main.todos'))


@main_bp.route('/todos/status/<int:todo_id>/<status>')
def update_todo_status(todo_id, status):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    data = {'status': status}
    if status == '进行中':
        from datetime import datetime
        data['actual_start'] = datetime.now()
    elif status == '已完成':
        from datetime import datetime
        data['actual_end'] = datetime.now()

    diary_db.update_todo(todo_id, data)
    return redirect(url_for('main.todos'))


@main_bp.route('/todos/complete/<int:todo_id>', methods=['GET', 'POST'])
def complete_todo(todo_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        completion_note = request.form.get('completion_note', '')
        data = {
            'status': '已完成',
            'completion_note': completion_note
        }
        from datetime import datetime
        data['actual_end'] = datetime.now()

        diary_db.update_todo(todo_id, data)
        return redirect(url_for('main.todos'))

    todo = diary_db.get_todo_by_id(todo_id)
    if not todo:
        return redirect(url_for('main.todos'))

    return render_template('todo/complete_todo.html', todo=todo)


@main_bp.route('/todos/cancel/<int:todo_id>', methods=['GET', 'POST'])
def cancel_todo(todo_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        cancel_reason = request.form.get('cancel_reason', '')
        data = {
            'status': '取消',
            'cancel_reason': cancel_reason
        }

        diary_db.update_todo(todo_id, data)
        return redirect(url_for('main.todos'))

    todo = diary_db.get_todo_by_id(todo_id)
    if not todo:
        return redirect(url_for('main.todos'))

    return render_template('todo/cancel_todo.html', todo=todo)

# 打卡相关路由
@main_bp.route('/checkin')
def checkin():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    items = diary_db.get_all_checkin_items()
    stats = diary_db.get_checkin_stats()
    return render_template('checkin/checkin.html', items=items, stats=stats)


@main_bp.route('/checkin/create', methods=['GET', 'POST'])
def create_checkin_item():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        target_days_str = request.form.get('target_days', '0')
        target_days = int(target_days_str) if target_days_str.strip() else 0

        data = {
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'frequency': request.form.get('frequency', 'daily'),
            'target_days': target_days,
            'icon': request.form.get('icon', '✅'),
            'color': request.form.get('color', '#3b82f6'),
            'is_active': True
        }

        diary_db.add_checkin_item(data)
        return redirect(url_for('main.checkin'))

    return render_template('checkin/create_checkin_item.html')


@main_bp.route('/checkin/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_checkin_item(item_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    item = diary_db.get_checkin_item_by_id(item_id)
    if not item:
        return redirect(url_for('main.checkin'))

    if request.method == 'POST':
        target_days_str = request.form.get('target_days', '0')
        target_days = int(target_days_str) if target_days_str.strip() else 0

        data = {
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'frequency': request.form.get('frequency', 'daily'),
            'target_days': target_days,
            'icon': request.form.get('icon', '✅'),
            'color': request.form.get('color', '#3b82f6'),
            'is_active': request.form.get('is_active') == 'on'
        }

        diary_db.update_checkin_item(item_id, data)
        return redirect(url_for('main.checkin'))

    return render_template('checkin/edit_checkin_item.html', item=item)


@main_bp.route('/checkin/delete/<int:item_id>')
def delete_checkin_item(item_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    diary_db.delete_checkin_item(item_id)
    return redirect(url_for('main.checkin'))


@main_bp.route('/checkin/do/<int:item_id>', methods=['GET', 'POST'])
def do_checkin(item_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        note = request.form.get('note', '')
        mood = request.form.get('mood', '')

        success, message = diary_db.add_checkin_record(item_id, note, mood)
        if success:
            return redirect(url_for('main.checkin'))
        else:
            item = diary_db.get_checkin_item_by_id(item_id)
            return render_template('checkin/do_checkin.html', item=item, error=message)

    item = diary_db.get_checkin_item_by_id(item_id)
    if not item:
        return redirect(url_for('main.checkin'))

    return render_template('checkin/do_checkin.html', item=item)


@main_bp.route('/checkin/history')
def checkin_history():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    item_id = request.args.get('item_id', type=int)
    days = request.args.get('days', 30, type=int)

    items = diary_db.get_all_checkin_items()
    records = diary_db.get_checkin_records(item_id, days)

    # 计算统计数据
    from datetime import datetime, timedelta
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # 获取统计数据
    total_records = len(diary_db.get_checkin_records(None, 365)) if diary_db else 0  # 一年内的总记录
    today_records = len(diary_db.get_checkin_records(None, 1)) if diary_db else 0  # 今日记录
    week_records = len(diary_db.get_checkin_records(None, 7)) if diary_db else 0  # 本周记录
    month_records = len(diary_db.get_checkin_records(None, 30)) if diary_db else 0  # 本月记录

    stats = {
        'total_records': total_records,
        'today_records': today_records,
        'week_records': week_records,
        'month_records': month_records
    }

    return render_template('checkin/checkin_history.html', items=items, records=records, selected_item_id=item_id, days=days, stats=stats)
