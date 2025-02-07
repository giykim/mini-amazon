from flask import current_app as app


class Product:
    def __init__(self, id, name, description, available):
        self.id = id
        self.name = name
        self.description = description
        self.available = available

    @staticmethod
    def get(id):
        rows = app.db.execute('''
            SELECT id, name, description, available
            FROM Products
            WHERE id = :id
            ''',
            id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        # Retrieves all currently available items at lowest price sold
        rows = app.db.execute('''
            SELECT p.id, p.name, p.description, p.available, MIN(s.price) as price
            FROM Products p
            JOIN SoldBy s on p.id = s.pid
            WHERE available = :available
            GROUP BY p.id
            ''',
            available=available)
        return rows
    
    @staticmethod
    def get_k_expensive(k):
        # Retrieves the top k most expensive items currently being sold
        rows = app.db.execute("""
            SELECT p.id, p.name, p.description, p.available, MIN(s.price) AS price
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            GROUP BY p.id
            ORDER BY MIN(s.price) DESC
            LIMIT :k
            """,
            k = k
        )
        return rows

    @staticmethod
    def search_products(query):
        # Retrieve products whose name is similar to user query
        rows = app.db.execute("""
            WITH Rating AS (
                SELECT p.pid, AVG(r.rating) AS rating, COUNT(r.rating) AS num_ratings
                FROM ProductReviews p
                JOIN Reviews r ON r.id = p.id
                GROUP BY p.pid
            ),
            Category AS (
                SELECT co.pid, c.id, c.name
                FROM Categories c
                JOIN CategoryOf co ON c.id = co.cid
            )
            SELECT p.id, p.name, p.description, p.image, MIN(s.price) as price,
                COALESCE(AVG(r.rating), 0) as rating, COUNT(r.rating) AS num_ratings,
                c.name as category
            FROM Products p
            LEFT JOIN SoldBy s ON p.id = s.pid
            LEFT JOIN Rating r ON p.id = r.pid
            LEFT JOIN Category c ON p.id = c.pid
            WHERE (LOWER(p.name) LIKE '%' || LOWER(:query) || '%'
                OR  LOWER(p.description) LIKE '%' || LOWER(:query) || '%')
                AND p.available IS TRUE
            GROUP BY p.id, c.name
            """,
            query = query
        )
        return rows
    
    @staticmethod
    def get_product_info(pid):
        # retrieve rating and characterestic info on specified product
        rows = app.db.execute("""
            WITH Rating AS (
                SELECT p.pid, AVG(r.rating) AS rating, COUNT(r.rating) AS num_ratings
                FROM ProductReviews p
                JOIN Reviews r ON r.id = p.id
                GROUP BY p.pid
            )
            SELECT p.name, p.description, p.id, p.image,
                COALESCE(r.rating, 0) AS rating, COALESCE(r.num_ratings, 0) as num_ratings
            FROM Products AS p
            LEFT JOIN Rating r ON p.id = r.pid
            WHERE p.id = :pid
            """,
            pid = pid
        )
        return rows
    
    @staticmethod
    def get_user_products(uid):
        # Retrieve products created by a specified user along with related reviews and info
        rows = app.db.execute("""
            WITH Rating AS (
                SELECT p.pid, AVG(r.rating) AS rating, COUNT(r.rating) AS num_ratings
                FROM ProductReviews p
                JOIN Reviews r ON r.id = p.id
                GROUP BY p.pid
            )
            SELECT p.id, p.name, p.description, p.image, s.price,
                COALESCE(r.rating, 0) AS rating, COALESCE(r.num_ratings, 0) as num_ratings
            FROM Products p
            JOIN CreatedProduct c ON p.id = c.pid
            LEFT JOIN SoldBy s ON p.id = s.pid
            LEFT JOIN Rating r ON p.id = r.pid
            WHERE c.uid = :uid
            ORDER BY p.name
            """,
            uid = uid
        )
        return rows
    
    @staticmethod
    def get_seller_info(pid):
        # Retrieve sellers and associated stocking info for sellers that sell a specified product
        rows = app.db.execute("""
            SELECT u.id as id, u.firstname AS sellerfirst, u.lastname AS sellerlast, b.quantity, b.price
            FROM Products AS p
            JOIN SoldBy AS b ON p.id = b.pid
            JOIN Users AS u ON u.id = b.sid
            WHERE p.id = :pid
                AND b.quantity > 0
            ORDER BY b.price ASC
            """,
            pid = pid
        )
        return rows
    
    @staticmethod
    def get_seller_quant(pid, sid):
        # Retrieve quantity of specified item sold by specified seller
        rows = app.db.execute("""
            SELECT quantity
            FROM Soldby
            WHERE sid = :sid AND pid = :pid
            """,
            pid = pid,
            sid = sid
        )
        return rows

    
    @staticmethod
    def get_creator_info(pid):
        # Retrieve info of the creator of a specified user created product
        rows = app.db.execute("""
            SELECT c.uid, u.firstname, u.lastname
            FROM CreatedProduct c
            JOIN Users u ON c.uid = u.id
            WHERE c.pid = :pid
            """,
            pid = pid
        )
        return rows
    
    @staticmethod
    def get_review_by_id(review_id):
        # Retrieve review info by id
        rows = app.db.execute('''
            SELECT * FROM Reviews
            WHERE id = :review_id
        ''', 
        review_id=review_id)
        return rows
    
    @staticmethod
    def get_review_info(pid):
        # Retrieve aggregate review information for a specified product
        rows = app.db.execute("""
            SELECT r1.id AS id, u1.firstname AS reviewfirst, u1.lastname AS reviewlast, r1.rating, 
                              r1.description AS ratingdescrip, r1.time_created, COALESCE(SUM(h.value), 0) AS helpfulness
            FROM Products AS p
            JOIN ProductReviews AS r ON p.id = r.pid
            JOIN Reviews AS r1 ON r1.id = r.id
            JOIN Users AS u1 ON u1.id = r.uid
            LEFT JOIN Helpfulness AS h ON h.rid = r.id
            WHERE p.id = :pid
            GROUP BY r1.id, u1.firstname, u1.lastname, r1.rating, r1.description, r1.time_created
            """,
            pid = pid
        )
        return rows
    
    @staticmethod
    def get_helpfulness(review_id):
        # Retrieve helpfulness of an individual review
        rows = app.db.execute("""
            SELECT COALESCE(SUM(value), 0) AS votes
            FROM Helpfulness
            WHERE rid = :review_id
            """, 
            review_id=review_id
        )
        return rows[0][0]
    
    @staticmethod
    def get_user_vote(review_id, user_id):
        rows = app.db.execute("""
            SELECT value 
            FROM Helpfulness
            WHERE rid = :review_id AND uid = :user_id
            """, 
            review_id=review_id, 
            user_id=user_id
        )
        return rows[0][0] if rows else None

    @staticmethod
    def update_vote(review_id, user_id, value):
        # Update the helpfulness score of a review
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
    def new_product(name, description, uid):
        # create a new user created product to product table and add to product tables
        pid = app.db.execute("""
            SELECT id
            FROM Products
            WHERE name=:name
        """,
            name=name
        )

        if pid:
            return pid[0][0], False

        result = app.db.execute("""
            INSERT INTO Products (name, description)
            VALUES (:name, :description)
            RETURNING id
        """, 
            name=name,
            description=description
        )

        pid = result[0][0]

        app.db.execute("""
            INSERT INTO CreatedProduct (pid, uid)
            VALUES (:pid, :uid)
        """, 
            pid=pid,
            uid=uid
        )

        return pid, True
    
    @staticmethod
    def update_product(pid, name, description):
        # Update product info
        """
        Update product info with new info
        """
        app.db.execute("""
            UPDATE Products
            SET name = :name, description = :description
            WHERE id = :pid
        """, 
            pid=pid, 
            name=name, 
            description=description
        )
    
    @staticmethod
    def set_category(pid, cid):
        """
        Set category of product
        """
        # Check if row corresponding to current product id exists
        row = app.db.execute("""
            SELECT 1
            FROM CategoryOf
            WHERE pid=:pid
        """, 
            pid=pid,
        )

        # If there is a row that exists, just update existing row
        if row:
            app.db.execute("""
                UPDATE CategoryOf
                SET cid = :cid
                WHERE pid = :pid
            """, 
                pid=pid, 
                cid=cid
            )
        # If there is no row, insert a new row
        else:
            app.db.execute("""
                INSERT INTO CategoryOf (pid, cid)
                VALUES (:pid, :cid)
            """, 
                pid=pid, 
                cid=cid
            )

    @staticmethod
    def remove_category(pid):
        """
        Remove category of product
        """
        app.db.execute("""
            DELETE FROM CategoryOf
            WHERE pid = :pid
        """, 
            pid=pid
        )
    
    @staticmethod
    def get_user_votes_for_product(pid, user_id):
        rows = app.db.execute("""
            SELECT h.rid AS review_id, h.value AS vote_value
            FROM Helpfulness AS h
            JOIN ProductReviews AS pr ON pr.id = h.rid
            WHERE pr.pid = :pid AND h.uid = :user_id
        """, 
            pid=pid, 
            user_id=user_id
        )

        user_votes = {row[0]: row[1] for row in rows}
        return user_votes


    @staticmethod
    def has_bought(uid, pid):
        rows = app.db.execute("""
            SELECT 1
            FROM Purchases
            WHERE time_purchased IS NOT NULL
                AND uid = :uid
                AND pid = :pid
        """, 
            uid=uid, 
            pid=pid
        )

        if rows:
            return True
        return False
    
    @staticmethod
    def get_available_products_paginated(page, per_page=12, available=True):
        # Retrieve all currently available products and associated info in a format that facilitates pagination 
        offset = (page - 1) * per_page
        print(f"Fetching products for page {page} with OFFSET {offset} and LIMIT {per_page}")
        rows = app.db.execute('''
            WITH Rating AS (
                SELECT p.pid, AVG(r.rating) AS rating, COUNT(r.rating) AS num_ratings
                FROM ProductReviews p
                JOIN Reviews r ON r.id = p.id
                GROUP BY p.pid
            )
            SELECT p.id, p.name, p.description, p.image, p.available,
                MIN(s.price) AS price, COALESCE(r.rating, 0) AS rating, COALESCE(r.num_ratings, 0) as num_ratings
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            LEFT JOIN Rating r ON p.id = r.pid
            WHERE p.available = :available
            GROUP BY p.id, r.rating, r.num_ratings
            ORDER BY p.id
            LIMIT :per_page OFFSET :offset
            ''',
            per_page=per_page, offset=offset, available=available)
        print(f"Fetched {len(rows)} products for page {page}")
        return rows
    
    @staticmethod
    def count_available():
        # Get a tally of currently available products
        result = app.db.execute('''
            SELECT COUNT(DISTINCT p.id)
            FROM Products p
            JOIN SoldBy s ON p.id = s.pid
            WHERE available = TRUE
        ''')
        return result[0][0] if result else 0
    
    @staticmethod
    def get_reviews_paginated(pid, page, per_page=5):
        # Retrieve all reviews for a product in a format that facilitates pagination
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT r1.id AS id, u1.firstname AS reviewfirst, u1.lastname AS reviewlast, r1.rating, 
                r1.description AS ratingdescrip, r1.time_created, COALESCE(SUM(h.value), 0) AS helpfulness
            FROM Products AS p
            JOIN ProductReviews AS r ON p.id = r.pid
            JOIN Reviews AS r1 ON r1.id = r.id
            JOIN Users AS u1 ON u1.id = r.uid
            LEFT JOIN Helpfulness AS h ON h.rid = r.id
            WHERE p.id = :pid
            GROUP BY r1.id, u1.firstname, u1.lastname, r1.rating, r1.description, r1.time_created
            ORDER BY COALESCE(SUM(h.value), 0) DESC, r1.time_created DESC
            LIMIT :per_page OFFSET :offset
            ''',
            pid=pid, per_page=per_page, offset=offset
        )
        return rows

    @staticmethod
    def count_reviews(pid):
        # Provide a tally for reviews of a given product
        result = app.db.execute('''
            SELECT COUNT(r1.id)
            FROM ProductReviews AS r
            JOIN Reviews AS r1 ON r.id = r1.id
            WHERE r.pid = :pid
            ''',
            pid=pid
        )
        return result[0][0] if result else 0
    
    @staticmethod
    def get_product_category(pid):
        '''
        Returns id of category of product
        '''
        rows = app.db.execute('''
            SELECT c1.cid, c2.name
            FROM CategoryOf c1
            JOIN Categories c2 ON c1.cid = c2.id
            WHERE c1.pid = :pid
            ''',
            pid=pid
        )
        return rows
    
    @staticmethod
    def get_product_tags(pid):
        '''
        Returns tags of product
        '''
        rows = app.db.execute('''
            SELECT name
            FROM IsTagged
            WHERE pid = :pid
            ''',
            pid=pid
        )
        return rows
    
    @staticmethod
    def get_categories():
        '''
        Returns all rows of product categories
        '''
        rows = app.db.execute('''
            SELECT id, name
            FROM Categories AS r
            '''
        )
        return rows
    
    @staticmethod
    def add_tag(pid, tag):
        """
        Assign a new tag to the product
        """
        # Check if the tag exists in relation
        row = app.db.execute("""
            SELECT 1
            FROM Tags
            WHERE name = :tag
            """,
            tag=tag
        )

        # If tag doesn't exist, insert
        if not row:
            app.db.execute("""
                INSERT INTO Tags (name)
                VALUES (:tag)
                """,
                tag=tag
            )

        # Check if row exists in IsTagged relation
        row = app.db.execute("""
            SELECT 1
            FROM Tags
            WHERE name = :tag
            """,
            tag=tag
        )

        # Assign new tag to product
        app.db.execute("""
            INSERT INTO IsTagged (pid, name)
            VALUES (:pid, :tag)
            ON CONFLICT (pid, name) DO NOTHING;
            """,
            pid=pid,
            tag=tag
        )
    
    @staticmethod
    def remove_all_tags(pid):
        """
        Delete all tags from a product
        """
        # Delete all rows in IsTagged corresponding with product
        app.db.execute("""
            DELETE FROM IsTagged
            WHERE pid = :pid
            """,
            pid=pid
        )

    @staticmethod
    def get_product_ratings(pid):
        '''
        Returns ratings of product
        '''
        rows = app.db.execute('''
            SELECT r.rating
            FROM ProductReviews p
            JOIN Reviews r ON r.id = p.id
            WHERE p.pid = :pid
            ''',
            pid=pid
        )
        return rows
    
    @staticmethod
    def get_related_products(pid):
        '''
        Returns similar products based on category and tags
        '''
        rows = app.db.execute('''
            WITH Rating AS (
                SELECT p.pid, AVG(r.rating) AS rating, COUNT(r.rating) AS num_ratings
                FROM ProductReviews p
                JOIN Reviews r ON r.id = p.id
                GROUP BY p.pid
            )
            SELECT p.id, p.name, p.description, p.image, MIN(s.price) as price,
                COALESCE(r.rating, 0) AS rating, COALESCE(r.num_ratings, 0) as num_ratings
            FROM Products p
            JOIN CategoryOf c ON p.id = c.pid
            LEFT JOIN SoldBy s ON p.id = s.pid
            LEFT JOIN Rating r ON p.id = r.pid
            WHERE p.id <> :pid
                AND (
                    c.cid = (
                        SELECT cid 
                        FROM CategoryOf 
                        WHERE pid = :pid
                    )
                    OR EXISTS (
                        SELECT 1
                        FROM IsTagged t1
                        JOIN IsTagged t2 ON t1.name = t2.name
                        WHERE t1.pid = p.id
                            AND t2.pid = :pid
                    )
                )
            GROUP BY p.id, r.rating, r.num_ratings
            LIMIT 3;
            ''',
            pid=pid
        )
        return rows
