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
            SELECT uid, pid, sid, time_purchased, quantity
            FROM Purchases
            WHERE uid = :uid
            AND time_purchased >= :since
            ORDER BY time_purchased DESC
            ''',
            uid=uid,
            since=since
        )
        return [Purchase(*row) for row in rows]
