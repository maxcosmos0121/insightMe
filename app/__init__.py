from flask import Flask

from app.views import main_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # 生产环境请更换
    app.register_blueprint(main_bp)
    return app
