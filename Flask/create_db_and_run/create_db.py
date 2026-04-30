import sys
import os

# Добавляем корень проекта в пути поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from app.db.session import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Таблицы базы данных созданы")