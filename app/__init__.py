from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """
    Создает и конфигурирует экземпляр приложения Flask.
    """
    app = Flask(__name__)

    # Конфигурация базы данных из переменных окружения
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB')
    db_host = 'db'  # Имя сервиса из docker-compose

    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация расширений с приложением
    db.init_app(app)
    migrate.init_app(app, db)

    # Регистрация эндпоинтов (Blueprint)
    from . import routes
    app.register_blueprint(routes.api_bp)

    return app
