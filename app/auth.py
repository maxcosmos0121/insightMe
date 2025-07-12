import os
import sqlite3
from typing import Tuple

from werkzeug.security import generate_password_hash, check_password_hash


class UserAuth:
    def __init__(self):
        os.makedirs('users', exist_ok=True)
        self.auth_db_path = os.path.join('users', 'auth.db')
        self._init_auth_db()

    def _init_auth_db(self):
        """初始化用户认证数据库"""
        conn = sqlite3.connect(self.auth_db_path)
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """注册新用户"""
        if not username or not password:
            return False, "用户名和密码不能为空"

        if len(username) < 3:
            return False, "用户名至少需要3个字符"

        if len(password) < 6:
            return False, "密码至少需要6个字符"

        try:
            conn = sqlite3.connect(self.auth_db_path)
            cursor = conn.cursor()

            # 检查用户名是否已存在
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return False, "用户名已存在"

            # 创建用户
            password_hash = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )

            conn.commit()
            conn.close()

            # 创建用户专属数据库
            self._create_user_db(username)

            return True, "注册成功"

        except Exception as e:
            return False, f"注册失败: {str(e)}"

    def verify_user(self, username: str, password: str) -> Tuple[bool, str]:
        """验证用户登录"""
        if not username or not password:
            return False, "用户名和密码不能为空"

        try:
            conn = sqlite3.connect(self.auth_db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            conn.close()

            if not result:
                return False, "用户名不存在"

            password_hash = result[0]
            if check_password_hash(password_hash, password):
                return True, "登录成功"
            else:
                return False, "密码错误"

        except Exception as e:
            return False, f"登录失败: {str(e)}"

    def user_exists(self, username: str) -> bool:
        """检查用户是否存在"""
        try:
            conn = sqlite3.connect(self.auth_db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except:
            return False

    def _create_user_db(self, username: str):
        """为用户创建专属数据库"""
        from app.models import DiaryDB
        # 这里只是初始化数据库，不需要实际使用
        db = DiaryDB(username)
        db.db.close()
