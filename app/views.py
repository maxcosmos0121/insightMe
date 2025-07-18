from flask import Blueprint, render_template, request, redirect, url_for, session

from app.auth import UserAuth
from app.models import DiaryDB
from datetime import datetime
from collections import defaultdict

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


@main_bp.route('/inspiration', methods=['GET', 'POST'])
def inspiration():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    error = None
    inspirations = []
    file_path = f'inspiration_{session["username"]}.txt'
    # 处理POST请求，添加或删除灵感
    if request.method == 'POST':
        delete_time = request.form.get('delete_time')
        if delete_time:
            # 删除指定时间的灵感
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if not line.startswith(delete_time):
                            f.write(line)
            except FileNotFoundError:
                pass
            return redirect(url_for('main.inspiration'))
        else:
            content = request.form.get('content', '').strip()
            if not content:
                error = '内容不能为空'
            else:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t{content}\n")
                return redirect(url_for('main.inspiration'))
    # 读取历史灵感
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    inspirations.append({'datetime': parts[0], 'content': parts[1]})
    except FileNotFoundError:
        pass
    inspirations = inspirations[::-1]  # 新的在前
    return render_template('inspiration/history.html', inspirations=inspirations, error=error)


@main_bp.route('/inspiration/add', methods=['GET', 'POST'])
def inspiration_add():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    error = None
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            error = '内容不能为空'
        else:
            file_path = f'inspiration_{session["username"]}.txt'
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t{content}\n")
            return redirect(url_for('main.inspiration'))
    return render_template('inspiration/add.html', error=error, now=now)

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/wallets')
def wallets():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    wallets = db.Wallet.select().order_by(db.Wallet.created_at.desc())
    return render_template('finance/wallets.html', wallets=wallets)

@finance_bp.route('/wallet/add', methods=['GET', 'POST'])
def add_wallet():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        type_ = request.form.get('type', '').strip()
        balance = request.form.get('balance', '0').strip()
        remark = request.form.get('remark', '').strip()
        if not name or not type_:
            error = '钱包名称和类型不能为空'
        else:
            try:
                balance_val = float(balance)
            except ValueError:
                error = '金额格式不正确'
            else:
                db.Wallet.create(name=name, type=type_, balance=balance_val, remark=remark, user_id=1)  # user_id=1为示例，实际应取当前用户id
                return redirect(url_for('finance.wallets'))
    return render_template('finance/add_wallet.html', wallet=None, error=error)

@finance_bp.route('/wallet/edit/<int:wallet_id>', methods=['GET', 'POST'])
def edit_wallet(wallet_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    wallet = db.Wallet.get_or_none(db.Wallet.id == wallet_id)
    if not wallet:
        return redirect(url_for('finance.wallets'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        type_ = request.form.get('type', '').strip()
        balance = request.form.get('balance', '0').strip()
        remark = request.form.get('remark', '').strip()
        if not name or not type_:
            error = '钱包名称和类型不能为空'
        else:
            try:
                balance_val = float(balance)
            except ValueError:
                error = '金额格式不正确'
            else:
                wallet.name = name
                wallet.type = type_
                wallet.balance = balance_val
                wallet.remark = remark
                wallet.save()
                return redirect(url_for('finance.wallets'))
    return render_template('finance/add_wallet.html', wallet=wallet, error=error)

@finance_bp.route('/wallet/delete/<int:wallet_id>')
def delete_wallet(wallet_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    wallet = db.Wallet.get_or_none(db.Wallet.id == wallet_id)
    if wallet:
        wallet.delete_instance()
    return redirect(url_for('finance.wallets'))

@finance_bp.route('/wallet/<int:wallet_id>')
def wallet_detail(wallet_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    wallet = db.Wallet.get_or_none(db.Wallet.id == wallet_id)
    if not wallet:
        return redirect(url_for('finance.wallets'))
    records = db.FinanceRecord.select().where(db.FinanceRecord.wallet_id == wallet_id).order_by(db.FinanceRecord.time.desc())
    return render_template('finance/wallet_detail.html', wallet=wallet, records=records)

@finance_bp.route('/record/add/<int:wallet_id>', methods=['GET', 'POST'])
def add_record(wallet_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    wallet = db.Wallet.get_or_none(db.Wallet.id == wallet_id)
    wallets = db.Wallet.select().where(db.Wallet.id != wallet_id)
    if not wallet:
        return redirect(url_for('finance.wallets'))
    error = None
    if request.method == 'POST':
        record_type = request.form.get('record_type', '').strip()
        amount = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        time_str = request.form.get('time', '').strip()
        remark = request.form.get('remark', '').strip()
        to_wallet_id = request.form.get('to_wallet_id') if record_type == '转出' else None
        if not record_type or not amount or (record_type == '转出' and not to_wallet_id):
            error = '类型、金额和目标钱包（转出）不能为空'
        else:
            try:
                amount_val = float(amount)
                time_val = datetime.strptime(time_str, '%Y-%m-%dT%H:%M') if time_str else datetime.now()
            except ValueError:
                error = '金额或时间格式不正确'
            else:
                related_record_id = None
                if record_type == '支出':
                    wallet.balance -= amount_val
                    wallet.save()
                elif record_type == '收入':
                    wallet.balance += amount_val
                    wallet.save()
                elif record_type == '转出':
                    wallet.balance -= amount_val
                    wallet.save()
                    to_wallet = db.Wallet.get_or_none(db.Wallet.id == int(to_wallet_id))
                    if to_wallet:
                        to_wallet.balance += amount_val
                        to_wallet.save()
                        # 先插入转出，后插入转入，转入的related_record_id指向转出
                        out_record = db.FinanceRecord.create(wallet_id=wallet_id, user_id=1, record_type='转出', amount=amount_val, category=category, time=time_val, remark=remark, to_wallet_id=to_wallet_id)
                        in_record = db.FinanceRecord.create(wallet_id=to_wallet.id, user_id=1, record_type='转入', amount=amount_val, category=category, time=time_val, remark=f'来自{wallet.name}：{remark}', to_wallet_id=wallet_id, related_record_id=out_record.id)
                        out_record.related_record_id = in_record.id
                        out_record.save()
                        return redirect(url_for('finance.wallet_detail', wallet_id=wallet_id))
                if record_type != '转出':
                    db.FinanceRecord.create(wallet_id=wallet_id, user_id=1, record_type=record_type, amount=amount_val, category=category, time=time_val, remark=remark)
                return redirect(url_for('finance.wallet_detail', wallet_id=wallet_id))
    return render_template('finance/add_record.html', wallet=wallet, wallets=wallets, record=None, error=error)

@finance_bp.route('/record/edit/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    record = db.FinanceRecord.get_or_none(db.FinanceRecord.id == record_id)
    if not record:
        return redirect(url_for('finance.wallets'))
    wallet = db.Wallet.get_or_none(db.Wallet.id == record.wallet_id)
    wallets = db.Wallet.select().where(db.Wallet.id != wallet.id)
    error = None
    if request.method == 'POST':
        # 回滚原余额
        if record.record_type == '支出':
            wallet.balance += record.amount
            wallet.save()
        elif record.record_type == '收入':
            wallet.balance -= record.amount
            wallet.save()
        elif record.record_type == '转出':
            wallet.balance += record.amount
            wallet.save()
            # 同步删除原转入记录
            if record.related_record_id:
                in_record = db.FinanceRecord.get_or_none(db.FinanceRecord.id == record.related_record_id)
                if in_record:
                    to_wallet = db.Wallet.get_or_none(db.Wallet.id == in_record.wallet_id)
                    if to_wallet:
                        to_wallet.balance -= in_record.amount
                        to_wallet.save()
                    in_record.delete_instance()
        elif record.record_type == '转入':
            wallet.balance -= record.amount
            wallet.save()
            # 不允许直接编辑转入
        # 新数据
        record_type = request.form.get('record_type', '').strip()
        amount = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        time_str = request.form.get('time', '').strip()
        remark = request.form.get('remark', '').strip()
        to_wallet_id = request.form.get('to_wallet_id') if record_type == '转出' else None
        if not record_type or not amount or (record_type == '转出' and not to_wallet_id):
            error = '类型、金额和目标钱包（转出）不能为空'
        else:
            try:
                amount_val = float(amount)
                time_val = datetime.strptime(time_str, '%Y-%m-%dT%H:%M') if time_str else datetime.now()
            except ValueError:
                error = '金额或时间格式不正确'
            else:
                if record_type == '支出':
                    wallet.balance -= amount_val
                    wallet.save()
                    record.record_type = record_type
                    record.amount = amount_val
                    record.category = category
                    record.time = time_val
                    record.remark = remark
                    record.to_wallet_id = None
                    record.related_record_id = None
                    record.save()
                elif record_type == '收入':
                    wallet.balance += amount_val
                    wallet.save()
                    record.record_type = record_type
                    record.amount = amount_val
                    record.category = category
                    record.time = time_val
                    record.remark = remark
                    record.to_wallet_id = None
                    record.related_record_id = None
                    record.save()
                elif record_type == '转出':
                    wallet.balance -= amount_val
                    wallet.save()
                    to_wallet = db.Wallet.get_or_none(db.Wallet.id == int(to_wallet_id))
                    if to_wallet:
                        to_wallet.balance += amount_val
                        to_wallet.save()
                        # 新建转入记录
                        in_record = db.FinanceRecord.create(wallet_id=to_wallet.id, user_id=1, record_type='转入', amount=amount_val, category=category, time=time_val, remark=f'来自{wallet.name}：{remark}', to_wallet_id=wallet.id, related_record_id=record.id)
                        record.record_type = '转出'
                        record.amount = amount_val
                        record.category = category
                        record.time = time_val
                        record.remark = remark
                        record.to_wallet_id = to_wallet.id
                        record.related_record_id = in_record.id
                        record.save()
                return redirect(url_for('finance.wallet_detail', wallet_id=wallet.id))
    return render_template('finance/add_record.html', wallet=wallet, wallets=wallets, record=record, error=error)

@finance_bp.route('/record/delete/<int:record_id>')
def delete_record(record_id):
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    record = db.FinanceRecord.get_or_none(db.FinanceRecord.id == record_id)
    wallet_id = record.wallet_id if record else None
    if record:
        wallet = db.Wallet.get_or_none(db.Wallet.id == record.wallet_id)
        # 回滚余额
        if record.record_type == '支出':
            wallet.balance += record.amount
            wallet.save()
        elif record.record_type == '收入':
            wallet.balance -= record.amount
            wallet.save()
        elif record.record_type == '转出':
            wallet.balance += record.amount
            wallet.save()
            # 同步删除转入记录
            if record.related_record_id:
                in_record = db.FinanceRecord.get_or_none(db.FinanceRecord.id == record.related_record_id)
                if in_record:
                    to_wallet = db.Wallet.get_or_none(db.Wallet.id == in_record.wallet_id)
                    if to_wallet:
                        to_wallet.balance -= in_record.amount
                        to_wallet.save()
                    in_record.delete_instance()
        elif record.record_type == '转入':
            wallet.balance -= record.amount
            wallet.save()
        record.delete_instance()
    if wallet_id:
        return redirect(url_for('finance.wallet_detail', wallet_id=wallet_id))
    return redirect(url_for('finance.wallets'))

@finance_bp.route('/stats')
def stats():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    db = DiaryDB(session['username'])
    wallets = list(db.Wallet.select())
    records = list(db.FinanceRecord.select())
    # 总收入、总支出、结余
    total_income = sum(r.amount for r in records if r.record_type == '收入')
    total_expense = sum(r.amount for r in records if r.record_type == '支出')
    total_balance = sum(w.balance for w in wallets)
    # 分类统计
    category_income = defaultdict(float)
    category_expense = defaultdict(float)
    for r in records:
        if r.record_type == '收入':
            category_income[r.category or '未分类'] += r.amount
        elif r.record_type == '支出':
            category_expense[r.category or '未分类'] += r.amount
    # 月度收支趋势
    from datetime import datetime
    monthly_income = defaultdict(float)
    monthly_expense = defaultdict(float)
    for r in records:
        ym = r.time.strftime('%Y-%m')
        if r.record_type == '收入':
            monthly_income[ym] += r.amount
        elif r.record_type == '支出':
            monthly_expense[ym] += r.amount
    months = sorted(set(list(monthly_income.keys()) + list(monthly_expense.keys())))
    trend = [{'month': m, 'income': monthly_income[m], 'expense': monthly_expense[m]} for m in months]
    return render_template('finance/stats.html', wallets=wallets, total_income=total_income, total_expense=total_expense, total_balance=total_balance, category_income=category_income, category_expense=category_expense, trend=trend)
