from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify

from app.models import DiaryDB
from app.auth import UserAuth
from datetime import datetime, timedelta

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
            return render_template('register.html', error='所有字段都必须填写')
        
        if password != confirm_password:
            return render_template('register.html', error='两次输入的密码不一致')
        
        success, message = user_auth.register_user(username, password)
        if success:
            return redirect(url_for('main.login', registered='true'))
        else:
            return render_template('register.html', error=message)
    
    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='用户名和密码不能为空')
        
        success, message = user_auth.verify_user(username, password)
        if success:
            session['username'] = username
            return redirect(url_for('main.home'))
        else:
            return render_template('login.html', error=message)
    
    # 检查是否是从注册页面跳转过来的
    registered = request.args.get('registered')
    success_message = None
    if registered == 'true':
        success_message = '注册成功！请使用您的用户名和密码登录。'
    
    return render_template('login.html', success=success_message)


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
        'todo_stats': diary_db.get_todo_stats() if diary_db else {'total': 0, 'not_started': 0, 'in_progress': 0, 'completed': 0, 'cancelled': 0}
    }
    
    return render_template('home.html', user=user)


@main_bp.route('/diary', methods=['GET', 'POST'])
def diary():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    today = diary_db.today()
    questions = diary_db.get_questions()
    if request.method == 'POST':
        if diary_db.has_today_record():
            return render_template('diary.html', today=today, questions=questions, error='今天已经写过日记了')
        record = {key: request.form.get(key, '') for key, _ in questions}
        diary_db.add_record(record)
        return redirect(url_for('main.history'))
    return render_template('diary.html', today=today, questions=questions)


@main_bp.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    records = diary_db.get_all_records()
    return render_template('history.html', records=records)


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
        return render_template('profile.html', profile=profile, message=message)
    else:
        profile = diary_db.get_profile()
        return render_template('profile.html', profile=profile)


@main_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.login'))

# 待做清单相关路由
@main_bp.route('/todos')
def todos():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    # 获取筛选参数
    status_filter = request.args.get('status', '')
    
    # 获取所有任务并根据状态筛选
    all_todos = diary_db.get_all_todos()
    if status_filter:
        todos = [todo for todo in all_todos if todo['status'] == status_filter]
    else:
        todos = all_todos
    
    stats = diary_db.get_todo_stats()
    
        events = []
    for i, record in enumerate(diary_db.get_all_records()):
        date_str = record.get('date')  # 举例：'2025-07-10'
        if date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')  # 调整格式取决于你的实际字段
            except ValueError:
                continue  # 忽略格式不对的
            events.append({
                'id': str(i),
                'calendarId': '1',
                'title': record.get('mood') or '写了日记',
                'category': 'time',
                'start': dt.isoformat(),
                'end': (dt + timedelta(minutes=30)).isoformat()
            })
    return render_template('todos.html', todos=todos, stats=stats, current_filter=status_filter, events=events)


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
    
    return render_template('add_todo.html')


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
    
    return render_template('edit_todo.html', todo=todo)


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
    
    return render_template('complete_todo.html', todo=todo)


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
    
    return render_template('cancel_todo.html', todo=todo)
