from app import create_app
from app.views import finance_bp

app = create_app()

app.register_blueprint(finance_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

