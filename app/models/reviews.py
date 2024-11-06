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
