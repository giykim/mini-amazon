from flask import current_app as app


class Inventory:
    def __init__(self, sid, pid):
        self.sid = sid
        self.pid = pid

    @staticmethod
    def get_inventory(sid):
        rows = app.db.execute('''
            SELECT pid, quantity
            FROM Inventory
            WHERE sid = :sid
            ''',
            sid=sid)
        return rows

    @staticmethod
    def get_sellers(pid):
        rows = app.db.execute('''
            SELECT sid
            FROM Inventory
            WHERE pid = :pid
            ''',
            pid=pid)
        return rows
