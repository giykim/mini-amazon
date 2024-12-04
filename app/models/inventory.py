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
        if len(rows) < 1:
            return False
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
            SELECT p.id, p.name, p.description,
                i.quantity as stock_quantity, s.quantity as sell_quantity, s.price
            FROM Products p
            JOIN Inventory i ON p.id = i.pid
            LEFT JOIN SoldBy s ON p.id = s.pid
                AND s.sid = :sid
            WHERE i.sid = :sid
            ORDER BY p.name
        ''', sid=sid)
        return rows

    @staticmethod
    def get_selling(sid):
        rows = app.db.execute('''
            WITH Rating AS (
                SELECT p.pid, AVG(r.rating) AS rating, COUNT(r.rating) AS num_ratings
                FROM ProductReviews p
                JOIN Reviews r ON r.id = p.id
                GROUP BY p.pid
            )
            SELECT p.id, p.name, p.description, p.image, s.quantity, s.price,
                COALESCE(r.rating, 0) AS rating, COALESCE(r.num_ratings, 0) as num_ratings
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            LEFT JOIN Rating r ON p.id = r.pid
            WHERE s.sid = :sid
            ORDER BY s.price ASC
        ''',
        sid=sid)

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
    def update_stock(sid, pid, quantity):
        # Check if a row corresponding to the seller and product exists
        row = app.db.execute("""
            SELECT 1 
            FROM Inventory 
            WHERE sid = :sid AND pid = :pid
        """, 
            sid=sid,
            pid=pid
        )

        # If it doesn't, insert it into the relation
        if not row:
            app.db.execute("""
                INSERT INTO Inventory (sid, pid, quantity)
                VALUES (:sid, :pid, :quantity)
            """, 
                sid=sid,
                pid=pid, 
                quantity=quantity
            )
        else:
            app.db.execute("""
                UPDATE Inventory
                SET quantity = quantity + :quantity
                WHERE sid = :sid AND pid = :pid
            """, 
                sid=sid,
                pid=pid, 
                quantity=quantity
            )
    
    @staticmethod
    def update_sold_by(sid, pid, quantity, price):
        # Check if a row corresponding to the seller and product exists
        row = app.db.execute("""
            SELECT 1 
            FROM SoldBy 
            WHERE sid = :sid AND pid = :pid
        """, 
            sid=sid,
            pid=pid
        )

        # If it doesn't, insert it into the relation
        if not row:
            app.db.execute("""
                INSERT INTO SoldBy (sid, pid, quantity, price)
                VALUES (:sid, :pid, :quantity, :price)
            """, 
                sid=sid,
                pid=pid, 
                quantity=quantity,
                price=price
            )
        else:
            app.db.execute("""
                UPDATE SoldBy
                SET quantity = :quantity, price = :price
                WHERE sid = :sid AND pid = :pid
            """, 
                sid=sid,
                pid=pid, 
                quantity=quantity,
                price=price
            )

        # If quantity is 0, then want to remove from SoldBy relation
        if int(quantity) == 0:
            app.db.execute("""
                DELETE FROM SoldBy
                WHERE sid=:sid
                    AND pid=:pid
                """, 
                sid=sid,
                pid=pid,
            )

    @staticmethod
    def fulfill_order(pid, sid, uid, time_purchased, price):
        # Check if seller has enough of product in stock
        inventory_quantity = app.db.execute("""
            SELECT quantity
            FROM Inventory
            WHERE sid = :sid AND pid = :pid
        """, 
            sid=sid,
            pid=pid
        )[0].quantity

        # Update fulfilled column of purchased
        order_quantity = app.db.execute("""
            SELECT quantity
            FROM Purchases
            WHERE pid = :pid AND sid = :sid AND uid = :uid AND time_purchased = :time_purchased
        """, 
            pid=pid,
            sid=sid,
            uid=uid,
            time_purchased=time_purchased
        )[0].quantity

        if inventory_quantity < order_quantity:
            # If not enough, display an error
            return False
        else:
            # Update fulfilled column of purchased if enough quantity
            app.db.execute("""
                UPDATE Purchases
                SET fulfilled = TRUE
                WHERE pid = :pid AND sid = :sid AND uid = :uid AND time_purchased = :time_purchased
            """, 
                pid=pid,
                sid=sid,
                uid=uid,
                time_purchased=time_purchased
            )

            # Update balance of seller
            app.db.execute("""
                UPDATE Users
                SET balance = balance + :price
                WHERE id = :id
            """, 
                id=sid,
                price=price
            )

            # Update inventory quantity
            app.db.execute("""
                UPDATE Inventory
                SET quantity = :quantity
                WHERE pid = :pid AND sid = :sid
            """, 
                pid=pid,
                sid=sid,
                quantity=(inventory_quantity-order_quantity)
            )

            # Check if sold by quantity is more than in stock now
            sale_quantity = app.db.execute("""
                SELECT quantity
                FROM SoldBy
                WHERE sid = :sid AND pid = :pid
            """, 
                sid=sid,
                pid=pid
            )[0].quantity

            if inventory_quantity - order_quantity < sale_quantity:
                # If less inventory in stock than sale, clamp sale quantity
                app.db.execute("""
                    UPDATE SoldBy
                    SET quantity = quantity
                    WHERE pid = :pid AND sid = :sid
                """, 
                    pid=pid,
                    sid=sid,
                    quantity=(inventory_quantity-order_quantity)
                )

                # If quantity is 0, then want to remove from SoldBy relation
                if inventory_quantity - order_quantity == 0:
                    app.db.execute("""
                        DELETE FROM SoldBy
                        WHERE sid=:sid
                            AND pid=:pid
                        """, 
                        sid=sid,
                        pid=pid,
                    )

        return True
    
    @staticmethod
    def get_quantity(sid, pid):
        rows = app.db.execute("""
            SELECT quantity 
            FROM SoldBy 
            WHERE sid = :sid AND pid = :pid
            """, 
            sid=sid,
            pid=pid
        )
        return rows


    

        
    

        

        
