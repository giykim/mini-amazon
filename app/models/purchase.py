from datetime import datetime

from flask import current_app as app


class Purchase:
    def __init__(self, uid, pid, sid, time_purchased, quantity):
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.time_purchased = time_purchased
        self.quantity = quantity

    @staticmethod
    def get(uid, pid, sid):
        # retrieve time and quantity information of a purchase based on user, product, and seller
        rows = app.db.execute('''
            SELECT uid, pid, sid, time_purchased, quantity
            FROM Purchases
            WHERE uid = :uid,
                pid = :pid,
                sid = :sid,
            ''',
            uid = uid,
            pid = pid,
            sid = sid
        )
        return Purchase(*(rows[0])) if rows else None

    
    @staticmethod
    def get_all_by_uid(uid):
        # Retrieve all purchases of a specified user
        rows = app.db.execute('''
            SELECT pu.uid, pu.pid, pu.sid, pu.time_purchased, pu.quantity,
                pr.name AS product_name, u.firstname AS seller_first, u.lastname AS seller_last
            FROM Purchases pu
            JOIN Products pr ON pu.pid = pr.id
            JOIN Users u ON pu.sid = u.id
            WHERE uid = :uid
            ORDER BY time_purchased DESC
            ''',
            uid=uid
        )
        return rows
    

    @staticmethod
    def get_all_purchased_by_uid(uid):
        # Retrieve all purchases of a specified user but with price and fulfillment status
        rows = app.db.execute('''
            SELECT pu.uid, pu.pid, pu.sid, pu.time_purchased, pu.quantity, pu.price, pu.fulfilled,
                pr.name AS product_name, u.firstname AS seller_first, u.lastname AS seller_last
            FROM Purchases pu
            JOIN Products pr ON pu.pid = pr.id
            JOIN Users u ON pu.sid = u.id
            WHERE uid = :uid
                AND time_purchased IS NOT NULL
            ORDER BY time_purchased DESC
            ''',
            uid=uid
        )
        return rows


    @staticmethod
    def get_all_by_uid_since(uid, since):
        # Retrieve all purchases by a user after a specified date
        rows = app.db.execute('''
            SELECT pu.uid, pu.pid, pu.sid, pu.time_purchased, pu.quantity,
                pr.name AS product_name, u.firstname AS seller_first, u.lastname AS seller_last
            FROM Purchases pu
            JOIN Products pr ON pu.pid = pr.id
            JOIN Users u ON pu.sid = u.id
            WHERE uid = :uid
            AND time_purchased >= :since
            ORDER BY time_purchased DESC
            ''',
            uid=uid,
            since=since
        )
        return rows
    
    @staticmethod
    def get_cart(uid):
        # Retrieve all products added to cart but not yet purchased
        rows = app.db.execute('''
            SELECT pu.pid, pu.sid, pu.quantity, pr.name, pr.id, pr.description, pr.image,
                u.firstname AS seller_first, u.lastname AS seller_last, s.price
            FROM Purchases pu
            JOIN Products pr ON pr.id = pu.pid
            JOIN Users u ON pu.sid = u.id
            JOIN SoldBy s ON s.sid = pu.sid
                AND s.pid = pr.id
            WHERE time_purchased IS NULL
                AND uid=:uid
            ORDER BY pr.name ASC
            ''',
            uid=uid
        )
        return rows
    
    @staticmethod
    def add_to_cart(uid, pid, sid, quantity):
        # add a product to a specified user's cart from a given listing, or add to the quantity of an item in the cart if already in the cart
        existing_purchase = app.db.execute('''
            SELECT quantity
            FROM Purchases 
            WHERE uid = :uid
                AND pid = :pid
                AND sid = :sid
                AND time_purchased IS NULL
            ''',
            uid=uid,
            pid=pid,
            sid=sid
        )

        if existing_purchase:
            quantity = int(quantity)
            quantity += int(existing_purchase[0].quantity)
            app.db.execute('''
                UPDATE Purchases 
                SET quantity = :quantity 
                WHERE uid = :uid
                    AND pid = :pid
                    AND sid = :sid
                    AND time_purchased IS NULL
                ''',
                uid=uid,
                pid=pid,
                sid=sid,
                quantity=quantity
            )
        else:
            app.db.execute('''
                INSERT INTO Purchases (uid, pid, sid, time_purchased, quantity, price, fulfilled)
                VALUES (:uid, :pid, :sid, NULL, :quantity, 0, FALSE)
                ''',
                uid=uid,
                pid=pid,
                sid=sid,
                quantity=quantity
            )
    
    @staticmethod
    def remove_product(uid, pid, sid):
        # remove a product listing from the cart of specified user
        app.db.execute('''
            DELETE FROM Purchases
            WHERE uid=:uid
                AND pid=:pid
                AND sid=:sid
                AND time_purchased IS NULL;
            ''',
            uid=uid,
            pid=pid,
            sid=sid
        )

    @staticmethod
    def order_product(uid, pid, sid):
        # Submit an order to purchases to be reviewed by involved sellers
        time_purchased = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        app.db.execute('''
            UPDATE Purchases
            SET time_purchased = :time_purchased,
                price = (
                    SELECT s.price
                    FROM SoldBy s
                    WHERE s.sid = Purchases.sid
                    AND s.pid = Purchases.pid
                ) * 1.075
            WHERE uid = :uid
            AND pid = :pid
            AND sid = :sid
            AND time_purchased IS NULL
            ''',
            uid=uid,
            pid=pid,
            sid=sid,
            time_purchased=time_purchased
        )

        # Need sellers to fulfill order

    
    @staticmethod
    def get_paginated(uid, page, per_page):
        offset = (page - 1) * per_page

        rows = app.db.execute('''
            SELECT pu.uid, pu.pid, pu.sid, pu.time_purchased, pu.quantity,
                pr.name AS product_name, u.firstname AS seller_first, u.lastname AS seller_last
            FROM Purchases pu
            JOIN Products pr ON pu.pid = pr.id
            JOIN Users u ON pu.sid = u.id
            WHERE uid = :uid
            ORDER BY time_purchased DESC
            LIMIT :per_page OFFSET :offset
            ''',
            uid=uid,
            per_page=per_page,
            offset=offset
        )
        return rows
    
    @staticmethod
    def get_incoming_purchases(sid):
        rows = app.db.execute('''
            SELECT pu.uid, pu.pid, pu.sid, pu.time_purchased, pu.quantity, pu.price, pu.fulfilled,
                pr.name AS product_name, u.firstname AS seller_first, u.lastname AS seller_last
            FROM Purchases pu
            JOIN Products pr ON pu.pid = pr.id
            JOIN Users u ON pu.sid = u.id
            WHERE pu.sid = :sid
                AND pu.fulfilled = FALSE
            ORDER BY time_purchased DESC
            ''',
            sid=sid
        )
        return rows


    @staticmethod
    def has_bought_from(uid, sid):
        """
        Check if user (uid) has purchased a product from seller (sid)
        """
        # Check if a row corresponding to user and seller exists in relation
        row = app.db.execute('''
            SELECT 1
            FROM Purchases
            WHERE uid = :uid AND sid = :sid
            ''',
            uid=uid,
            sid=sid
        )
        
        # If row exists, return True
        return len(row) > 0
