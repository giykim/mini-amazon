from flask import current_app as app


class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def get(id):
        rows = app.db.execute('''
            SELECT id, name
            FROM Categories
            WHERE id = :id
            ''',
            id=id)
        return Category(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all():
        rows = app.db.execute('''
            SELECT id, name
            FROM Categories
            ''',
            available=available)
        return [Category(*row) for row in rows]
