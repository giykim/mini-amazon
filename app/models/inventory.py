from flask import current_app as app


class Inventory:
    def __init__(self, sid, pid, quantity):
        self.sid = sid
        self.pid = pid
        self.quantity = quantity

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
    
    @staticmethod 
    def get_product_detail(pid, sid):
        rows = app.db.execute('''
            WITH uinfo AS (
            SELECT id, firstname, lastname, email
            FROM Users WHERE id = :sid
            ),
            pinfo AS (
            SELECT id, name, description
            FROM Products
            ),
            stock_info AS (
            SELECT *
            FROM Inventory WHERE pid = :pid
            ),
            psinfo AS (
            SELECT p.name, p.description, s.quantity, s.sid
            FROM pinfo p 
            JOIN stock_info s on p.id = s.pid
            ),
            full_description AS (
            SELECT :pid as id, ps.name, ps.description, ps.quantity, u.firstname, u.lastname, u.email
            FROM psinfo ps
            JOIN uinfo u ON ps.sid = u.id
            )
            SELECT DISTINCT * FROM full_description;
            ''',
            pid=pid,sid=sid)
        return rows
    
    @staticmethod
    def get_inventory_details(sid):
        # Retrieves the full inventory for a seller
        rows = app.db.execute('''
            SELECT p.id, p.name, p.description, i.quantity
            FROM Products p
            JOIN Inventory i ON p.id = i.pid
            WHERE i.sid = :sid
        ''', sid=sid)
        return rows

    @staticmethod
    def get_sold_by_details_paginated(sid, page, per_page=12):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT p.id, p.name, p.description, s.quantity, s.price
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            WHERE s.sid = :sid
            ORDER BY s.price ASC
            LIMIT :per_page OFFSET :offset
        ''', sid=sid, per_page=per_page, offset=offset)
        return rows

    @staticmethod
    def count_sold_products(sid):
        rows = app.db.execute('''
            SELECT COUNT(*)
            FROM SoldBy
            WHERE sid = :sid
        ''', sid=sid)
        return rows[0][0] if rows else 0
    @staticmethod
    def set_quantity(sid, pid, q):
        rows = app.db.execute('''
            UPDATE Inventory
            SET quantity = q 
            WHERE sid = :sid AND pid = :pid
        ''', pid=pid,sid=sid)
        return rows[0][0] if rows else 0
    

        
    

        

        
