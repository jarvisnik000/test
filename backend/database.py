import os
from flask import g

def using_postgres():
    return 'DATABASE_URL' in os.environ

def get_db_path():
    if using_postgres():
        return None
    return os.environ.get('DB_PATH', 'notes.db')

def init_db():
    db = get_db()
    if using_postgres():
        with db.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        db.commit()
    else:
        with db:
            db.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.execute('''
                CREATE TRIGGER IF NOT EXISTS update_notes_timestamp
                AFTER UPDATE ON notes
                BEGIN
                    UPDATE notes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            ''')

def get_db():
    if 'db' not in g:
        if using_postgres():
            import psycopg2
            g.db = psycopg2.connect(os.environ['DATABASE_URL'])
        else:
            import sqlite3
            g.db = sqlite3.connect(
                get_db_path(),
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()