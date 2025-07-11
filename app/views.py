from flask import Blueprint, render_template, request, redirect, url_for, session

from app.models import DiaryDB

diary_db = None
main_bp = Blueprint('main', __name__)


@main_bp.before_request
def before_request():
    global diary_db
    username = session.get('username')
    if username:
        diary_db = DiaryDB(username)
    else:
        diary_db = None


@main_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return render_template('login.html', error='用户名不能为空')
        session['username'] = username
        return redirect(url_for('main.history'))  # 登录后跳转到历史记录
    return render_template('login.html')


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


@main_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.login'))
