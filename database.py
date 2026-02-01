import sqlite3
from pathlib import Path


class DataBase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / 'data' / 'data.db'

        self.db_path = Path(db_path)

        self.init_database()

    def init_database(self):
        '''Создаёт базу данных если её нет'''
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Включаем поддержку внешних ключей
            conn.execute("PRAGMA foreign_keys = ON;")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS level1 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    score INTEGER NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS level2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    score INTEGER NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS level3 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    score INTEGER NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def add_score_to_level(self, level: int, score: int):
        '''Добавляет новый счёт для игры по полученному уровню'''
        if level not in [1, 2, 3]:
            return

        table_name = f'level{level}'

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(f'''INSERT INTO {table_name} (score) VALUES ({score})''')

            conn.commit()

    def get_scores_for_level(self, level: int):
        '''Получает по полученному уровню счёт игры'''
        if level not in [1, 2, 3]:
            return

        table_name = f'level{level}'

        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                score_data = cur.execute(f'''SELECT * FROM {table_name}''').fetchall()

            return score_data

        except Exception as error:
            return error