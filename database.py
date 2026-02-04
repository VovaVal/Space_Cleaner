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

            cur = conn.cursor()

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

            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    ship_ind INTEGER NOT NULL,
                    sound_background_music INTEGER NOT NULL,
                    sound_shoot_sound INTEGER NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS all_levels_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    score INTEGER NOT NULL,
                    level INTEGER NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

            if not cur.execute('''SELECT * FROM settings''').fetchone():  # если данные уже имеются
                self.set_initial_data_to_settings()

    def set_initial_data_to_settings(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''INSERT INTO settings VALUES (0, 1, 1)''')

    def set_data_to_settings(self, ship_ind=None, sound_background_music=None, sound_shoot_sound=None):
        '''Добавляет/изменяет данные в настройках(1 - значит музыка будет играть, а у корабля это просто индексы скина)'''
        with sqlite3.connect(self.db_path) as conn:
            if ship_ind is not None:
                conn.execute(f'''UPDATE settings SET ship_ind = {ship_ind}''')
            if sound_background_music is not None:
                conn.execute(f'''UPDATE settings SET sound_background_music = {sound_background_music}''')
            if sound_shoot_sound is not None:
                conn.execute(f'''UPDATE settings SET sound_shoot_sound = {sound_shoot_sound}''')

            conn.commit()

    def clear_records(self, level=None, all_levels=None):
        '''Очищает рекорды под чистую'''
        with sqlite3.connect(self.db_path) as conn:
            if level == 1 or all_levels is not None:
                conn.execute('''DELETE FROM level1''')
            if level == 2 or all_levels is not None:
                conn.execute('''DELETE FROM level2''')
            if level == 3 or all_levels is not None:
                conn.execute('''DELETE FROM level3''')

            conn.commit()

    def get_data_from_settings(self, ship_ind=None, sound_background_music=None, sound_shoot_sound=None):
        '''Возвращает необходимые данные из настроек'''
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            data = cur.execute('''SELECT * FROM settings''').fetchall()

        if ship_ind is not None:
            return data[0][0]
        elif sound_background_music is not None:
            return data[0][1]
        elif sound_shoot_sound is not None:
            return data[0][-1]

    def add_score_to_level(self, level: int, score: int):
        '''Добавляет новый счёт для игры по полученному уровню'''
        if level not in [1, 2, 3]:
            return

        table_name = f'level{level}'

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(f'''INSERT INTO {table_name} (score) VALUES ({score})''')

            conn.commit()

        self.add_score_to_all_levels(level, score)

    def add_score_to_all_levels(self, level: int, score: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f'''INSERT INTO all_levels_data (score, level) VALUES ({score}, {level})''')

            conn.commit()

    def get_scores_for_level(self, level: int):
        '''Получает по полученному уровню счёт игры'''
        if level not in [1, 2, 3]:
            return

        table_name = f'level{level}'

        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                score_data = cur.execute(f'''SELECT score FROM {table_name}''').fetchall()

            return score_data

        except Exception as error:
            return error