from flask import current_app as app


class Review:
    def __init__(self, id, rating, description, time_created):
        self.id = id
        self.rating = rating
        self.description = description
        self.time_created = time_created

    @staticmethod
    def get(id):
        rows = app.db.execute('''
            SELECT id, rating, description, time_created
            FROM Reviews
            WHERE id = :id
            ''',
            id=id)
        return Review(*(rows[0])) if rows is not None else None
    
    @staticmethod
    def get_recent_reviews(reviewerid):
        rows = app.db.execute("""
            WITH HelpfulnessValue AS (
                SELECT rid, COALESCE(SUM(value), 0) AS helpfulness
                FROM Helpfulness
                GROUP BY rid
            )
            SELECT 
                r.id,
                CASE
                 WHEN p.pid IS NULL THEN 'Seller'
                 ELSE 'Product'
                END AS review_type,
                CASE
                 WHEN p1.name IS NULL THEN u.firstname || ' ' || u.lastname
                 ELSE p1.name
                END AS Name,
                r.rating, r.description, r.time_created, COALESCE(h.helpfulness, 0) AS helpfulness
            FROM Reviews r
            LEFT JOIN SellerReviews s ON r.id = s.id
            LEFT JOIN ProductReviews p ON r.id = p.id
            LEFT JOIN Products AS p1 ON p1.id = p.pid
            LEFT JOIN Users AS u ON u.id = s.sid
            LEFT JOIN HelpfulnessValue h ON h.rid = r.id
            WHERE s.uid = :reviewerid or p.uid = :reviewerid
            ORDER BY r.time_created DESC
            LIMIT 5
            """,
            reviewerid = reviewerid
        )
        return rows

    
    @staticmethod
    def new_product_review(uid, pid, rating, description):
        already_exists = app.db.execute("""
            SELECT 1
            FROM ProductReviews
            WHERE uid=:uid
                AND pid=:pid
        """, 
            uid=uid,
            pid=pid
        )

        if already_exists:
            return True

        result = app.db.execute("""
            INSERT INTO Reviews (rating, description, time_created)
            VALUES (:rating, :description, CURRENT_TIMESTAMP)
            RETURNING id
        """, 
            rating=rating,
            description=description
        )

        id = result[0][0]

        app.db.execute("""
            INSERT INTO ProductReviews (id, uid, pid)
            VALUES (:id, :uid, :pid)
        """, 
            id=id,
            uid=uid,
            pid=pid
        )

        return False
    

    @staticmethod
    def new_seller_review(uid, sid, rating, description):
        already_exists = app.db.execute("""
            SELECT 1
            FROM SellerReviews
            WHERE uid=:uid
                AND sid=:sid
        """, 
            uid=uid,
            sid=sid
        )

        if already_exists:
            return True

        result = app.db.execute("""
            INSERT INTO Reviews (rating, description, time_created)
            VALUES (:rating, :description, CURRENT_TIMESTAMP)
            RETURNING id
        """, 
            rating=rating,
            description=description
        )

        id = result[0][0]

        app.db.execute("""
            INSERT INTO SellerReviews (id, uid, sid)
            VALUES (:id, :uid, :sid)
        """, 
            id=id,
            uid=uid,
            sid=sid
        )

        return False
    

    # In reviews.py
    @staticmethod
    def get_seller_reviews_paginated(sid, page, per_page=5):
        offset = (page - 1) * per_page
        rows = app.db.execute("""
                SELECT r.id, u.firstname, u.lastname, r.rating, r.description, r.time_created, COALESCE(SUM(h.value), 0) AS helpfulness
                FROM Reviews AS r
                JOIN SellerReviews AS s ON r.id = s.id
                JOIN Users AS u ON s.uid = u.id
                LEFT JOIN Helpfulness AS h ON h.rid = r.id
                WHERE s.sid = :sid
                GROUP BY r.id, u.firstname, u.lastname, r.rating, r.description, r.time_created
                ORDER BY r.time_created DESC
                LIMIT :per_page OFFSET :offset
            """,
            sid=sid, per_page=per_page, offset=offset
        )
        return rows

    @staticmethod
    def count_seller_reviews(sid):
        rows = app.db.execute("""
            SELECT COUNT(*)
            FROM SellerReviews
            WHERE sid = :sid
        """, sid=sid)
        return rows[0][0] if rows else 0

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
    def delete_review(rid):
        """
        Delete review from Reviews, SellerReviews, ProductReviews relation with corresponding id
        """
        app.db.execute("""
            DELETE FROM Helpfulness
            WHERE rid=:rid
            """, 
            rid=rid
        )

        app.db.execute("""
            DELETE FROM SellerReviews
            WHERE id=:rid
            """, 
            rid=rid
        )

        app.db.execute("""
            DELETE FROM ProductReviews
            WHERE id=:rid
            """, 
            rid=rid
        )
        
        app.db.execute("""
            DELETE FROM Reviews
            WHERE id=:rid
            """, 
            rid=rid
        )

    @staticmethod
    def get_review_info(rid):
        rows = app.db.execute("""
            WITH HelpfulnessValue AS (
                SELECT rid, COALESCE(SUM(value), 0) AS helpfulness
                FROM Helpfulness
                GROUP BY rid
            )
            SELECT 
                r.id,
                CASE
                WHEN p.pid IS NULL THEN 'Seller'
                ELSE 'Product'
                END AS review_type,
                CASE
                WHEN p1.name IS NULL THEN u.firstname || ' ' || u.lastname
                ELSE p1.name
                END AS Name,
                r.rating, r.description, r.time_created, COALESCE(h.helpfulness, 0) AS helpfulness
            FROM Reviews r
            LEFT JOIN SellerReviews s ON r.id = s.id
            LEFT JOIN ProductReviews p ON r.id = p.id
            LEFT JOIN Products AS p1 ON p1.id = p.pid
            LEFT JOIN Users AS u ON u.id = s.sid
            LEFT JOIN HelpfulnessValue h ON h.rid = r.id
            WHERE r.id = :rid
            """,
            rid = rid
        )
        return rows
    
    @staticmethod
    def update_review(rid, rating, description):
        app.db.execute("""
            UPDATE Reviews
            SET rating=:rating, description=:description
            WHERE id = :rid
        """, 
            rid=rid, 
            rating=rating, 
            description=description
        )