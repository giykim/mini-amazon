from flask import current_app as app


class Product:
    def __init__(self, id, name, description, available):
        self.id = id
        self.name = name
        self.description = description
        self.available = available

    @staticmethod
    def get(id):
        rows = app.db.execute('''
            SELECT id, name, description, available
            FROM Products
            WHERE id = :id
            ''',
            id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
            SELECT id, name, description, available
            FROM Products
            WHERE available = :available
            ''',
            available=available)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def get_k_expensive(k):
        rows = app.db.execute("""
            SELECT p.id, p.name, p.description, p.available, MAX(s.price) AS max_price
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            GROUP BY p.id
            ORDER BY MAX(s.price) DESC
            LIMIT :k
            """,
            k = k
        )
        return rows
