from database import get_db, using_postgres

def _fetchone(cur_or_db):
    if using_postgres():
        row = cur_or_db.fetchone()
        if row:
            columns = [desc[0] for desc in cur_or_db.description]
            return dict(zip(columns, row))
        return None
    return cur_or_db.fetchone()

def _fetchall(cur_or_db):
    if using_postgres():
        rows = cur_or_db.fetchall()
        if not rows:
            return []
        columns = [desc[0] for desc in cur_or_db.description]
        return [dict(zip(columns, row)) for row in rows]
    return [dict(row) for row in cur_or_db.fetchall()]

def _p():
    return '%s' if using_postgres() else '?'

class Note:
    @staticmethod
    def get_all():
        db = get_db()
        p = _p()
        if using_postgres():
            with db.cursor() as cur:
                cur.execute(f'SELECT * FROM notes ORDER BY updated_at DESC')
                return _fetchall(cur)
        else:
            rows = db.execute(f'SELECT * FROM notes ORDER BY updated_at DESC').fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(note_id):
        db = get_db()
        p = _p()
        if using_postgres():
            with db.cursor() as cur:
                cur.execute(f'SELECT * FROM notes WHERE id = {p}', (note_id,))
                return _fetchone(cur)
        else:
            row = db.execute(f'SELECT * FROM notes WHERE id = {p}', (note_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(title, content, tags):
        db = get_db()
        p = _p()
        if using_postgres():
            with db.cursor() as cur:
                cur.execute(
                    f'INSERT INTO notes (title, content, tags) VALUES ({p}, {p}, {p}) RETURNING id',
                    (title, content, ','.join(tags) if tags else '')
                )
                note_id = cur.fetchone()[0]
            db.commit()
            return note_id
        else:
            cursor = db.execute(
                f'INSERT INTO notes (title, content, tags) VALUES ({p}, {p}, {p})',
                (title, content, ','.join(tags) if tags else '')
            )
            db.commit()
            return cursor.lastrowid

    @staticmethod
    def update(note_id, title, content, tags):
        db = get_db()
        p = _p()
        if using_postgres():
            with db.cursor() as cur:
                cur.execute(
                    f'UPDATE notes SET title = {p}, content = {p}, tags = {p} WHERE id = {p}',
                    (title, content, ','.join(tags) if tags else '', note_id)
                )
            db.commit()
        else:
            db.execute(
                f'UPDATE notes SET title = {p}, content = {p}, tags = {p} WHERE id = {p}',
                (title, content, ','.join(tags) if tags else '', note_id)
            )
            db.commit()

    @staticmethod
    def delete(note_id):
        db = get_db()
        p = _p()
        if using_postgres():
            with db.cursor() as cur:
                cur.execute(f'DELETE FROM notes WHERE id = {p}', (note_id,))
            db.commit()
        else:
            db.execute(f'DELETE FROM notes WHERE id = {p}', (note_id,))
            db.commit()

    @staticmethod
    def search_by_tag(tag):
        db = get_db()
        p = _p()
        if using_postgres():
            with db.cursor() as cur:
                cur.execute(
                    f'SELECT * FROM notes WHERE tags LIKE {p} ORDER BY updated_at DESC',
                    (f'%{tag}%',)
                )
                return _fetchall(cur)
        else:
            rows = db.execute(
                f'SELECT * FROM notes WHERE tags LIKE {p} ORDER BY updated_at DESC',
                (f'%{tag}%',)
            ).fetchall()
            return [dict(row) for row in rows]