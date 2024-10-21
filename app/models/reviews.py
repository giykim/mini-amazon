from flask import current_app as app


class Review:
    def __init__(self, id, rating, description, time_created, helpfulness):
        self.id = id
        self.rating = rating
        self.description = description
        self.time_created = time_created
        self.helpfulness = helpfulness

    @staticmethod
    def get(id):
        rows = app.db.execute('''
            SELECT id, rating, description, time_created, helpfulness
            FROM Reviews
            WHERE id = :id
            ''',
            id=id)
        return Review(*(rows[0])) if rows is not None else None
    
    @staticmethod
    def get_recent_reviews(reviewerid):
        rows = app.db.execute("""
            SELECT 
                CASE
                 WHEN p.pid IS NULL THEN 'Seller'
                 ELSE 'Product'
                END AS review_type,
                CASE
                 WHEN p1.name IS NULL THEN u.firstname || ' ' || u.lastname
                 ELSE p1.name
                END AS Name,
                r.rating, r.description, r.time_created, r.helpfulness
            FROM Reviews r
            JOIN SellerReviews s ON r.id = s.id
            JOIN ProductReviews p ON r.id = p.id
            JOIN Products AS p1 ON p1.id = p.pid
            JOIN Users AS u ON u.id = s.sid
            WHERE s.uid = :reviewerid or p.uid = :reviewerid
            ORDER BY r.time_created DESC
            LIMIT 5
            """,
            reviewerid = reviewerid
        )
        return rows
