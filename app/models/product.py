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
            LEFT JOIN SoldBy s ON p.id = s.pid
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
    def get_user_products(uid):
        rows = app.db.execute("""
            SELECT p.id, p.name, p.description
            FROM Products p
            JOIN CreatedProduct c ON p.id = c.pid
            WHERE c.uid = :uid
            """,
            uid = uid
        )
        return rows
    
    @staticmethod
    def get_seller_info(pid):
        rows = app.db.execute("""
            SELECT u.id as id, u.firstname AS sellerfirst, u.lastname AS sellerlast, b.quantity, b.price
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
    def get_creator_info(pid):
        rows = app.db.execute("""
            SELECT c.uid, u.firstname, u.lastname
            FROM CreatedProduct c
            JOIN Users u ON c.uid = u.id
            WHERE c.pid = :pid
            """,
            pid = pid
        )
        return rows
    
    @staticmethod
    def get_review_by_id(review_id):
        rows = app.db.execute('''
            SELECT * FROM Reviews
            WHERE id = :review_id
        ''', 
        review_id=review_id)
        return rows
    
    @staticmethod
    def get_review_info(pid):
        rows = app.db.execute("""
            SELECT r1.id AS id, u1.firstname AS reviewfirst, u1.lastname AS reviewlast, r1.rating, 
                              r1.description AS ratingdescrip, r1.time_created, COALESCE(SUM(h.value), 0) AS helpfulness
            FROM Products AS p
            JOIN ProductReviews AS r ON p.id = r.pid
            JOIN Reviews AS r1 ON r1.id = r.id
            JOIN Users AS u1 ON u1.id = r.uid
            LEFT JOIN Helpfulness AS h ON h.rid = r.id
            WHERE p.id = :pid
            GROUP BY r1.id, u1.firstname, u1.lastname, r1.rating, r1.description, r1.time_created
            """,
            pid = pid
        )
        return rows
    
    @staticmethod
    def get_helpfulness(review_id):
        rows = app.db.execute("""
            SELECT COALESCE(SUM(value), 0) AS votes
            FROM Helpfulness
            WHERE rid = :review_id
            """, 
            review_id=review_id
        )
        return rows[0][0]
    
    @staticmethod
    def get_user_vote(review_id, user_id):
        rows = app.db.execute("""
            SELECT value 
            FROM Helpfulness
            WHERE rid = :review_id AND uid = :user_id
            """, 
            review_id=review_id, 
            user_id=user_id
        )
        return rows[0][0] if rows else None

    @staticmethod
    def update_vote(review_id, user_id, value):
        app.db.execute("""
            UPDATE Helpfulness
            SET value = :value
            WHERE rid = :review_id AND uid = :user_id
        """, 
            value=value, 
            review_id=review_id, 
            user_id=user_id
        )

    @staticmethod
    def add_vote(review_id, user_id, value):
        app.db.execute("""
            INSERT INTO Helpfulness (rid, uid, value)
            VALUES (:review_id, :user_id, :value)
        """, 
            review_id=review_id, 
            user_id=user_id, 
            value=value
        )

    @staticmethod
    def new_product(name, description, uid):
        pid = app.db.execute("""
            SELECT id
            FROM Products
            WHERE name=:name
        """,
            name=name
        )

        if pid:
            return pid[0][0], False

        result = app.db.execute("""
            INSERT INTO Products (name, description)
            VALUES (:name, :description)
            RETURNING id
        """, 
            name=name,
            description=description
        )

        pid = result[0][0]

        app.db.execute("""
            INSERT INTO CreatedProduct (pid, uid)
            VALUES (:pid, :uid)
        """, 
            pid=pid,
            uid=uid
        )

        return pid, True
    
    @staticmethod
    def get_user_votes_for_product(pid, user_id):
        rows = app.db.execute("""
            SELECT h.rid AS review_id, h.value AS vote_value
            FROM Helpfulness AS h
            JOIN ProductReviews AS pr ON pr.id = h.rid
            WHERE pr.pid = :pid AND h.uid = :user_id
        """, 
            pid=pid, 
            user_id=user_id
        )

        user_votes = {row[0]: row[1] for row in rows}
        return user_votes


    @staticmethod
    def has_bought(uid, pid):
        rows = app.db.execute("""
            SELECT 1
            FROM Purchases
            WHERE time_purchased IS NOT NULL
                AND uid = :uid
                AND pid = :pid
        """, 
            uid=uid, 
            pid=pid
        )

        if rows:
            return True
        return False
    
    @staticmethod
    def get_available_products_paginated(page, per_page=12, available=True):
        offset = (page - 1) * per_page
        print(f"Fetching products for page {page} with OFFSET {offset} and LIMIT {per_page}")
        rows = app.db.execute('''
            SELECT p.id, p.name, p.description, p.available, MIN(s.price) AS price
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            WHERE p.available = :available
            GROUP BY p.id
            ORDER BY p.id
            LIMIT :per_page OFFSET :offset
            ''',
            per_page=per_page, offset=offset, available=available)
        print(f"Fetched {len(rows)} products for page {page}")
        return rows
    
    @staticmethod
    def count_available():
        result = app.db.execute('''
            SELECT COUNT(DISTINCT p.id)
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            WHERE available = TRUE
        ''')
        return result[0][0] if result else 0
    
    @staticmethod
    def get_reviews_paginated(pid, page, per_page=5):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT r1.id AS id, u1.firstname AS reviewfirst, u1.lastname AS reviewlast, r1.rating, 
                r1.description AS ratingdescrip, r1.time_created, COALESCE(SUM(h.value), 0) AS helpfulness
            FROM Products AS p
            JOIN ProductReviews AS r ON p.id = r.pid
            JOIN Reviews AS r1 ON r1.id = r.id
            JOIN Users AS u1 ON u1.id = r.uid
            LEFT JOIN Helpfulness AS h ON h.rid = r.id
            WHERE p.id = :pid
            GROUP BY r1.id, u1.firstname, u1.lastname, r1.rating, r1.description, r1.time_created
            ORDER BY r1.time_created DESC
            LIMIT :per_page OFFSET :offset
            ''',
            pid=pid, per_page=per_page, offset=offset
        )
        return rows

    @staticmethod
    def count_reviews(pid):
        result = app.db.execute('''
            SELECT COUNT(r1.id)
            FROM ProductReviews AS r
            JOIN Reviews AS r1 ON r.id = r1.id
            WHERE r.pid = :pid
            ''',
            pid=pid
        )
        return result[0][0] if result else 0

    
    # @staticmethod
    # def get_sellers_for_product(pid):
    #     rows = app.db.execute("""
    #         SELECT u.firstname AS firstname, u.lastname AS lastname, s.quantity AS quantity, s.price AS price
    #         FROM SoldBy AS s
    #         JOIN Users AS u ON s.sid = u.id
    #         WHERE s.pid = :pid
    #     """, 
    #         pid=pid
    #     )
    #     return rows
