from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class Seller:
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(id):
        rows = app.db.execute("""
            SELECT id
            FROM Sellers
            WHERE id = :id
            """,
            id=id
        )
        return Seller(*(rows[0])) if rows else None
    
    @staticmethod
    def get_seller_ratings(sid):
        '''
        Returns ratings of seller
        '''
        rows = app.db.execute('''
            SELECT r.rating
            FROM SellerReviews s
            JOIN Reviews r ON r.id = s.id
            WHERE s.sid = :sid
            ''',
            sid=sid
        )
        return rows
    
    
