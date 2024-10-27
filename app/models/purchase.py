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
    def get_all_by_uid_since(uid, since):
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
        rows = app.db.execute('''
            SELECT pu.pid, pu.sid, pu.quantity, pr.name, pr.id, pr.description,
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
                INSERT INTO Purchases (uid, pid, sid, time_purchased, quantity)
                VALUES (:uid, :pid, :sid, NULL, :quantity)
                ''',
                uid=uid,
                pid=pid,
                sid=sid,
                quantity=quantity
            )
    
    @staticmethod
    def remove_product(uid, pid, sid):
        rows = app.db.execute('''
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
