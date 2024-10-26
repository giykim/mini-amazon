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
            SELECT p.id, p.name, p.description, p.available, MIN(s.price) as price
            FROM Products p
            JOIN SoldBy s on p.id = s.pid
            WHERE available = :available
            GROUP BY p.id
            ''',
            available=available)
        return rows
    
    @staticmethod
    def get_k_expensive(k):
        rows = app.db.execute("""
            SELECT p.id, p.name, p.description, p.available, MIN(s.price) AS price
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            GROUP BY p.id
            ORDER BY MIN(s.price) DESC
            LIMIT :k
            """,
            k = k
        )
        return rows

    @staticmethod
    def search_products(query):
        rows = app.db.execute("""
            SELECT p.id, p.name, p.description, MIN(s.price) as price
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            WHERE name LIKE '%' || :query || '%'
                AND available IS TRUE
            GROUP BY p.id
            """,
            query = query
        )
        return rows
    
    @staticmethod
    def get_product_info(pid):
        rows = app.db.execute("""
            SELECT p.name, p.description, p.id
            FROM Products AS p
            WHERE p.id = :pid
            """,
            pid = pid
        )
        return rows
    
    @staticmethod
    def get_seller_info(pid):
        rows = app.db.execute("""
            SELECT u.id as id, u.firstname AS sellerfirsta, u.lastname AS sellerlast, b.quantity, b.price
            FROM Products AS p
            JOIN SoldBy AS b ON p.id = b.pid
            JOIN Users AS u ON u.id = b.sid
            WHERE p.id = :pid
            ORDER BY b.price ASC
            """,
            pid = pid
        )
        return rows
    
    @staticmethod
    def get_review_info(pid):
        rows = app.db.execute("""
            SELECT u1.firstname AS reviewfirst, u1.lastname AS reviewlast, r1.rating, 
                              r1.description AS ratingdescrip, r1.time_created, r1.helpfulness
            FROM Products AS p
            JOIN ProductReviews AS r ON p.id = r.pid
            JOIN Reviews AS r1 ON r1.id = r.id
            JOIN Users AS u1 ON u1.id = r.uid
            WHERE p.id = :pid
            """,
            pid = pid
        )
        return rows